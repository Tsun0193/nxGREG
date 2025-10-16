from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from core import GraphData
from data import resolve_input_path
from loading import Neo4jLoader
from pipelines import run_llm_pipeline, run_rule_based_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reset or rebuild the Neo4j knowledge graph."
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild the graph from the input after wiping.",
    )
    parser.add_argument(
        "--method",
        choices=["rule", "llm"],
        default="rule",
        help="Pipeline to use for rebuild (default: rule).",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to the input/markdown file to parse (default: ctc-data-translated/input-en.md).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    logger = logging.getLogger(__name__)

    load_dotenv()

    neo4j_url = os.environ["NEO4J_URL"]
    neo4j_username = os.environ["NEO4J_USERNAME"]
    neo4j_password = os.environ["NEO4J_PASSWORD"]

    loader = Neo4jLoader(neo4j_url, neo4j_username, neo4j_password)
    try:
        loader.load(GraphData(), wipe=True)
    finally:
        loader.close()
    logger.info("Knowledge graph wiped.")

    if args.rebuild:
        input_path, input_source = resolve_input_path(args.input)
        logger.info("Using input file (%s): %s", input_source, input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"input file not found at {input_path}")
        if args.method == "rule":
            run_rule_based_pipeline(
                input_path,
                wipe=False,
                neo4j_url=neo4j_url,
                neo4j_username=neo4j_username,
                neo4j_password=neo4j_password,
            )
            logger.info("Knowledge graph rebuilt with rule-based pipeline.")
        else:
            summary = run_llm_pipeline(
                input_path,
                wipe=False,
                neo4j_url=neo4j_url,
                neo4j_username=neo4j_username,
                neo4j_password=neo4j_password,
            )
            logger.info("LLM pipeline completed after wipe.")
            print("LLM pipeline output after wipe:")
            print(summary)


if __name__ == "__main__":
    main()
