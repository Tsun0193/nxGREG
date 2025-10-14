from __future__ import annotations

import logging
from pathlib import Path
from textwrap import dedent
from typing import Optional

from llm import generate_response
from .loader import Neo4jLoader
from .parser import KnowledgeGraphParser
from .progress import ProgressBar

logger = logging.getLogger(__name__)


def _build_prompt(readme_contents: str) -> str:
    return dedent(
        f"""
        You are a knowledge graph architect. Read the provided markdown documentation and
        produce a concise summary that highlights:
        - Key entities or modules mentioned.
        - Important relationships or workflows.
        - Any data structures, validation rules, or integration points.

        Respond in markdown with clear headings and bullet points.

        Documentation:
        ---
        {readme_contents}
        ---
        """
    ).strip()


def run_llm_pipeline(
    readme_path: Path,
    *,
    wipe: bool = False,
    neo4j_url: Optional[str] = None,
    neo4j_username: Optional[str] = None,
    neo4j_password: Optional[str] = None,
) -> str:
    """
    Use the LLM-based pipeline to analyze the README, return a summary, and optionally load the graph.

    When Neo4j connection details are provided, the README is also parsed via the rule-based parser and
    the resulting graph is loaded into Neo4j before returning the summary.
    """
    should_load = bool(neo4j_url and neo4j_username and neo4j_password)
    steps = [
        "Read README",
        "Build prompt",
        "Request completion",
        "Parse README",
        "Load graph into Neo4j" if should_load else "Skip Neo4j load",
    ]
    progress = ProgressBar(len(steps), prefix="LLM pipeline")
    logger.info("LLM pipeline starting for %s", readme_path)

    progress.advance("Reading README")
    readme_contents = readme_path.read_text(encoding="utf-8")
    logger.info("Loaded README (%d characters)", len(readme_contents))

    progress.advance("Building prompt")
    prompt = _build_prompt(readme_contents)
    logger.info("Prompt prepared (%d characters)", len(prompt))

    progress.advance("Requesting completion")
    response = generate_response(prompt)
    logger.info("LLM response received (%d characters)", len(response))

    progress.advance("Parsing README")
    parser = KnowledgeGraphParser(readme_path)
    graph = parser.parse()
    logger.info("Parsed %d nodes and %d relationships", len(graph.nodes), len(graph.relationships))

    if should_load:
        assert neo4j_url is not None
        assert neo4j_username is not None
        assert neo4j_password is not None
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

    logger.info("LLM pipeline finished")
    return response
