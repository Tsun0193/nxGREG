from __future__ import annotations

from typing import Optional
import os

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
                
                # Helper function to escape string values for Cypher
                def escape_cypher_value(value):
                    if value is None:
                        return "null"
                    elif isinstance(value, bool):
                        return "true" if value else "false"
                    elif isinstance(value, (int, float)):
                        return str(value)
                    elif isinstance(value, str):
                        # Escape quotes and backslashes
                        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                        return f'"{escaped}"'
                    else:
                        # Convert other types to string
                        escaped = str(value).replace('\\', '\\\\').replace('"', '\\"')
                        return f'"{escaped}"'
                
                # Build query with literal values instead of parameters
                query_parts = [f"MERGE (n{label_expr} {{uid: $uid}})"]
                
                if properties:
                    set_clauses = []
                    for key, value in properties.items():
                        escaped_value = escape_cypher_value(value)
                        set_clauses.append(f"n.`{key}` = {escaped_value}")
                    query_parts.append("SET " + ", ".join(set_clauses))
                
                full_query = " ".join(query_parts)
                
                session.run(full_query, {"uid": uid})
            for rel in graph.relationships:
                # Helper function to escape string values for Cypher
                def escape_cypher_value(value):
                    if value is None:
                        return "null"
                    elif isinstance(value, bool):
                        return "true" if value else "false"
                    elif isinstance(value, (int, float)):
                        return str(value)
                    elif isinstance(value, str):
                        # Escape quotes and backslashes
                        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                        return f'"{escaped}"'
                    else:
                        # Convert other types to string
                        escaped = str(value).replace('\\', '\\\\').replace('"', '\\"')
                        return f'"{escaped}"'
                
                # Build query with literal values
                query_parts = [
                    "MATCH (a:GraphNode {uid: $start_uid}), (b:GraphNode {uid: $end_uid})",
                    f"MERGE (a)-[r:{rel.rel_type}]->(b)"
                ]
                
                if rel.properties:
                    set_clauses = []
                    for key, value in rel.properties.items():
                        escaped_value = escape_cypher_value(value)
                        set_clauses.append(f"r.`{key}` = {escaped_value}")
                    query_parts.append("SET " + ", ".join(set_clauses))
                
                full_query = " ".join(query_parts)
                params = {
                    "start_uid": rel.start_key,
                    "end_uid": rel.end_key,
                }
                session.run(full_query, params)


if __name__ == "__main__":
    neo4j_url = os.getenv("NEO4J_URL")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    graph = Neo4jLoader(uri=neo4j_url, user=neo4j_username, password=neo4j_password)
    