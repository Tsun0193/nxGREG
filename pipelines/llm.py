from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

from clients import generate_response
from data import resolve_readme_path
from loading import Neo4jLoader
from parsing import KnowledgeGraphParser
from prompts import (
    build_mermaid_to_cypher_prompt,
    build_summary_prompt,
)
from utils import ProgressBar

logger = logging.getLogger(__name__)


def _build_prompt(readme_contents: str) -> Tuple[str, str]:
    prompt = build_mermaid_to_cypher_prompt(readme_contents)
    if prompt:
        return prompt, "mermaid_to_cypher"
    return build_summary_prompt(readme_contents), "summary"


def run_llm_pipeline(
    readme_path: Optional[Path] = None,
    *,
    wipe: bool = False,
    neo4j_url: Optional[str] = None,
    neo4j_username: Optional[str] = None,
    neo4j_password: Optional[str] = None,
) -> str:
    """
    Use the LLM-based pipeline to analyze the README and return generated content.

    When Mermaid diagrams are present, the LLM receives a prompt template that asks for Cypher statements.
    Otherwise, the LLM produces a structured summary. When Neo4j connection details are provided, the
    README is also parsed via the rule-based parser and the resulting graph is loaded before returning.
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
    resolved_readme, readme_source = resolve_readme_path(readme_path)
    if not resolved_readme.exists():
        raise FileNotFoundError(f"README file not found at {resolved_readme}")
    logger.info("LLM pipeline using README (%s): %s", readme_source, resolved_readme)

    progress.advance("Reading README")
    readme_contents = resolved_readme.read_text(encoding="utf-8")
    logger.info("Loaded README (%d characters)", len(readme_contents))

    progress.advance("Building prompt")
    prompt, prompt_mode = _build_prompt(readme_contents)
    logger.info("Prompt prepared using '%s' template (%d characters)", prompt_mode, len(prompt))

    progress.advance("Requesting completion")
    response = generate_response(prompt)
    logger.info("LLM response received (%d characters)", len(response))

    progress.advance("Parsing README")
    parser = KnowledgeGraphParser(resolved_readme)
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
