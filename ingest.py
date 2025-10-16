from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import List, Set

from dotenv import load_dotenv

from pipelines import run_llm_pipeline, run_rule_based_pipeline
from tqdm import tqdm

logger = logging.getLogger(__name__)


def _collect_input_files(input_path: Path, pattern: str) -> List[Path]:
    expanded = input_path.expanduser()
    if expanded.is_file():
        return [expanded.resolve()]
    if expanded.is_dir():
        matches = sorted(path for path in expanded.rglob(pattern) if path.is_file())
        if not matches:
            raise ValueError(f"Directory {expanded} matched no files with pattern {pattern!r}")
        seen: Set[Path] = set()
        unique: List[Path] = []
        for match in matches:
            resolved = match.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique.append(resolved)
        return unique
    raise FileNotFoundError(f"Input path not found: {expanded}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest one or more markdown files into the Neo4j knowledge graph without wiping existing data."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Markdown file or directory to ingest. Directories are searched recursively using --pattern.",
    )
    parser.add_argument(
        "--pattern",
        default="*.md",
        help="Glob pattern used when expanding directories (default: *.md).",
    )
    parser.add_argument(
        "--method",
        choices=["rule", "llm"],
        default="rule",
        help="Pipeline to use for ingestion (default: rule).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    logger.info("Starting ingestion with method '%s'", args.method)

    load_dotenv()

    neo4j_url = os.getenv("NEO4J_URL")
    neo4j_username = os.getenv("NEO4J_USERNAME")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    missing_env = [name for name, value in [
        ("NEO4J_URL", neo4j_url),
        ("NEO4J_USERNAME", neo4j_username),
        ("NEO4J_PASSWORD", neo4j_password),
    ] if not value]
    if missing_env:
        missing_str = ", ".join(missing_env)
        raise RuntimeError(f"Missing required environment variable(s): {missing_str}")

    input_files = _collect_input_files(args.input, args.pattern)
    logger.info("Resolved %d input file(s) for ingestion.", len(input_files))

    pipeline = run_rule_based_pipeline if args.method == "rule" else run_llm_pipeline
    for index, input_file in enumerate(tqdm(input_files, desc="Ingestion", unit="file"), start=1):
        logger.info("Ingesting [%d/%d]: %s", index, len(input_files), input_file)
        if args.method == "rule":
            pipeline(
                input_file,
                wipe=False,
                neo4j_url=neo4j_url,
                neo4j_username=neo4j_username,
                neo4j_password=neo4j_password,
            )
        else:
            summary = pipeline(
                input_file,
                wipe=False,
                neo4j_url=neo4j_url,
                neo4j_username=neo4j_username,
                neo4j_password=neo4j_password,
            )
            logger.info("LLM pipeline completed for %s", input_file)
            if summary.strip():
                print(f"\n--- LLM output for {input_file} ---\n{summary}\n")

    logger.info("Ingestion complete.")


if __name__ == "__main__":
    main()
