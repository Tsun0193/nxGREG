from __future__ import annotations

from typing import Optional

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - driver may be absent during static analysis
    GraphDatabase = None  # type: ignore[assignment]

from core import GraphData


class Neo4jLoader:
    """Loads the parsed graph data into Neo4j."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        if GraphDatabase is None:
            raise RuntimeError(
                "The neo4j Python driver is not installed. Install it with 'pip install neo4j'."
            )
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def load(self, graph: GraphData, wipe: bool = False) -> None:
        with self.driver.session() as session:
            session.run(
                "CREATE CONSTRAINT graph_node_uid IF NOT EXISTS "
                "FOR (n:GraphNode) REQUIRE n.uid IS UNIQUE"
            )
            if wipe:
                session.run("MATCH (n) DETACH DELETE n")
            for node in graph.nodes.values():
                label_expr = ":" + ":".join(sorted(set(node.labels)))
                properties = dict(node.properties)
                uid = properties.pop("uid")
                parameters = {"uid": uid}
                set_clause = ""
                if properties:
                    parameters["props"] = properties
                    set_clause = " SET n += $props"
                session.run(
                    f"MERGE (n{label_expr} {{uid: $uid}}){set_clause}",
                    parameters,
                )
            for rel in graph.relationships:
                params = {
                    "start_uid": rel.start_key,
                    "end_uid": rel.end_key,
                    "props": rel.properties,
                }
                set_clause = " SET r += $props" if rel.properties else ""
                session.run(
                    (
                        "MATCH (a:GraphNode {uid: $start_uid}), (b:GraphNode {uid: $end_uid}) "
                        f"MERGE (a)-[r:{rel.rel_type}]->(b){set_clause}"
                    ),
                    params,
                )
