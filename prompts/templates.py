from __future__ import annotations

import re
from textwrap import dedent
from typing import List, Optional, Tuple


def _extract_heading_for_index(markdown: str, index: int) -> str:
    """
    Return the closest Markdown heading that appears before the given index.

    Falls back to a generic label when no heading is present.
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", flags=re.MULTILINE)
    heading_matches = list(heading_pattern.finditer(markdown[:index]))
    if not heading_matches:
        return "Global Context"
    return heading_matches[-1].group(2).strip()


def extract_mermaid_sections(markdown: str) -> List[Tuple[str, str]]:
    """
    Extract Mermaid diagrams and their contextual headings from markdown text.

    Returns:
        A list of (context_heading, mermaid_diagram) tuples in the order they appear.
    """
    sections: List[Tuple[str, str]] = []
    mermaid_pattern = re.compile(r"```mermaid\s*(.*?)```", flags=re.DOTALL)
    for match in mermaid_pattern.finditer(markdown):
        context = _extract_heading_for_index(markdown, match.start())
        diagram = match.group(1).strip()
        if diagram:
            sections.append((context, diagram))
    return sections


MERMAID_TO_CYPHER_PROMPT_TEMPLATE = dedent(
    """
    You are a senior Neo4j and Cypher specialist. Analyze each Mermaid diagram using its
    provided context and produce Cypher statements that create the nodes and relationships.

    Requirements:
    - Preserve the intent of the diagram and use meaningful labels/properties.
    - Avoid duplicating nodes; reuse identifiers where appropriate.
    - Group related Cypher statements using comments that reference the context.
    - Wrap each Cypher block in ```cypher fences.

    Use the following context/diagram pairs:

    {context_blocks}
    """
).strip()


def build_mermaid_to_cypher_prompt(markdown: str) -> Optional[str]:
    """
    Construct a prompt that instructs the LLM to translate Mermaid diagrams to Cypher.

    Returns None when no Mermaid diagrams are present.
    """
    sections = extract_mermaid_sections(markdown)
    if not sections:
        return None

    blocks: List[str] = []
    for context, diagram in sections:
        block = dedent(
            f"""
            # context
            {context}
            # mermaid graph
            ```mermaid
            {diagram}
            ```
            """
        ).strip()
        blocks.append(block)

    context_blocks = "\n\n".join(blocks)
    return MERMAID_TO_CYPHER_PROMPT_TEMPLATE.format(context_blocks=context_blocks)


SUMMARY_PROMPT_TEMPLATE = dedent(
    """
    You are a knowledge graph architect. Read the provided markdown documentation and
    produce a concise summary that highlights:
    - Key entities or modules mentioned.
    - Important relationships or workflows.
    - Any data structures, validation rules, or integration points.

    Respond in markdown with clear headings and bullet points.

    Documentation:
    ---
    {documentation}
    ---
    """
).strip()


def build_summary_prompt(markdown: str) -> str:
    """Fallback summary prompt when no Mermaid diagrams are present."""
    return SUMMARY_PROMPT_TEMPLATE.format(documentation=markdown)
