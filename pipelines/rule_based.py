from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from core import GraphData
from data import resolve_input_path
from loading import Neo4jLoader
from parsing import KnowledgeGraphParser
from tqdm import tqdm

logger = logging.getLogger(__name__)


def run_rule_based_pipeline(
    readme_path: Optional[Path] = None,
    *,
    wipe: bool = False,
    neo4j_url: Optional[str] = None,
    neo4j_username: Optional[str] = None,
    neo4j_password: Optional[str] = None,
) -> GraphData:
    """Parse markdown via the regex/rule-based parser and optionally load to Neo4j."""
    steps = [
        "Initialize parser",
        "Parse input",
    ]
    should_load = bool(neo4j_url and neo4j_username and neo4j_password)
    if should_load:
        steps.append("Load graph into Neo4j")
    else:
        steps.append("Skip Neo4j load")

    with tqdm(total=len(steps), desc="Rule pipeline", unit="step") as progress:
        def advance(step_description: str) -> None:
            progress.set_postfix_str(step_description)
            progress.update()

        resolved_input, input_source = resolve_input_path(readme_path)
        if not resolved_input.exists():
            raise FileNotFoundError(f"Input file not found at {resolved_input}")
        logger.info("Rule-based pipeline using input (%s): %s", input_source, resolved_input)

        advance("Initializing parser")
        parser = KnowledgeGraphParser(resolved_input)

        advance("Parsing input")
        graph = parser.parse()
        logger.info("Parsed %d nodes and %d relationships", len(graph.nodes), len(graph.relationships))

        if should_load:
            advance("Loading graph into Neo4j")
            logger.info("Loading graph into Neo4j at %s", neo4j_url)
            loader = Neo4jLoader(neo4j_url, neo4j_username, neo4j_password)
            try:
                loader.load(graph, wipe=wipe)
            finally:
                loader.close()
            logger.info("Neo4j load complete")
        else:
            advance("Neo4j load skipped")
            logger.info("Neo4j connection details missing; skipping load")

    logger.info("Rule-based pipeline finished")
    return graph
