from __future__ import annotations

import os
import argparse
from pathlib import Path

from dotenv import load_dotenv

from src.cli import run_pipeline
from src.graph import GraphData
from src.loader import Neo4jLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset or rebuild the Neo4j knowledge graph.")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the graph from the README after wiping.",
    )
    args = parser.parse_args()

    load_dotenv()

    neo4j_url = os.environ["NEO4J_URL"]
    neo4j_username = os.environ["NEO4J_USERNAME"]
    neo4j_password = os.environ["NEO4J_PASSWORD"]

    loader = Neo4jLoader(neo4j_url, neo4j_username, neo4j_password)
    try:
        loader.load(GraphData(), wipe=True)
    finally:
        loader.close()
    print("Knowledge graph wiped.")

    if args.rebuild:
        readme_path = Path(os.getenv("CTC_README_PATH", "ctc-data-translated/readme.md"))
        if not readme_path.exists():
            raise FileNotFoundError(f"README file not found at {readme_path}")
        run_pipeline(
            readme_path,
            wipe=False,
            neo4j_url=neo4j_url,
            neo4j_username=neo4j_username,
            neo4j_password=neo4j_password,
        )
        print("Knowledge graph rebuilt.")


if __name__ == "__main__":
    main()
