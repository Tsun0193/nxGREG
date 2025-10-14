from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .graph import GraphData
from .loader import Neo4jLoader
from .parser import KnowledgeGraphParser
from .progress import ProgressBar

logger = logging.getLogger(__name__)


def run_rule_based_pipeline(
    readme_path: Path,
    *,
    wipe: bool = False,
    neo4j_url: Optional[str] = None,
    neo4j_username: Optional[str] = None,
    neo4j_password: Optional[str] = None,
) -> GraphData:
    """Parse markdown via the regex/rule-based parser and optionally load to Neo4j."""
    steps = [
        "Initialize parser",
        "Parse README",
    ]
    should_load = bool(neo4j_url and neo4j_username and neo4j_password)
    if should_load:
        steps.append("Load graph into Neo4j")
    else:
        steps.append("Skip Neo4j load")

    progress = ProgressBar(len(steps), prefix="Rule pipeline")
    logger.info("Rule-based pipeline starting for %s", readme_path)

    progress.advance("Initializing parser")
    parser = KnowledgeGraphParser(readme_path)

    progress.advance("Parsing README")
    graph = parser.parse()
    logger.info("Parsed %d nodes and %d relationships", len(graph.nodes), len(graph.relationships))

    if should_load:
        progress.advance("Loading graph into Neo4j")
        logger.info("Loading graph into Neo4j at %s", neo4j_url)
        loader = Neo4jLoader(neo4j_url, neo4j_username, neo4j_password)
        try:
            loader.load(graph, wipe=wipe)
        finally:
            loader.close()
        logger.info("Neo4j load complete")
    else:
        progress.advance("Neo4j load skipped")
        logger.info("Neo4j connection details missing; skipping load")

    logger.info("Rule-based pipeline finished")
    return graph
