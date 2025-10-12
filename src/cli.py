from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .graph import GraphData
from .loader import Neo4jLoader
from .parser import KnowledgeGraphParser


def format_summary(graph: GraphData) -> str:
    summary = {
        "nodes": len(graph.nodes),
        "relationships": len(graph.relationships),
        "labels": sorted(
            {
                label
                for node in graph.nodes.values()
                for label in node.labels
            }
        ),
        "relationship_types": sorted({rel.rel_type for rel in graph.relationships}),
    }
    return json.dumps(summary, indent=2)


def run_pipeline(
    readme_path: Path,
    *,
    wipe: bool = False,
    neo4j_url: Optional[str] = None,
    neo4j_username: Optional[str] = None,
    neo4j_password: Optional[str] = None,
) -> GraphData:
    parser = KnowledgeGraphParser(readme_path)
    graph = parser.parse()

    if neo4j_url and neo4j_username and neo4j_password:
        loader = Neo4jLoader(neo4j_url, neo4j_username, neo4j_password)
        try:
            loader.load(graph, wipe=wipe)
        finally:
            loader.close()

    return graph


def main() -> None:
    load_dotenv()

    readme_path = Path(os.getenv("CTC_README_PATH", "ctc-data-translated/readme.md"))
    if not readme_path.exists():
        raise FileNotFoundError(f"README file not found at {readme_path}")

    neo4j_url = os.getenv("NEO4J_URL")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    wipe_flag = os.getenv("NEO4J_WIPE", "false").lower() in {"1", "true", "yes", "on"}

    graph = run_pipeline(
        readme_path,
        wipe=wipe_flag,
        neo4j_url=neo4j_url,
        neo4j_username=neo4j_username,
        neo4j_password=neo4j_password,
    )

    print(format_summary(graph))
    if not all([neo4j_url, neo4j_username, neo4j_password]):
        print("Neo4j connection details were not fully provided; ran in dry-run mode.")


if __name__ == "__main__":
    main()
