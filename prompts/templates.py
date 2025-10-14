from __future__ import annotations

import re
from textwrap import dedent
from typing import List, Optional, Tuple


def _extract_heading_path(markdown: str, index: int) -> List[str]:
    """
    Return the stacked Markdown heading titles that appear before the given index.

    Produces a hierarchy such as ["Error Handling", "Validation Failures"].
    """
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", flags=re.MULTILINE)
    stack: List[Tuple[int, str]] = []
    last_path: Optional[List[str]] = None
    for match in heading_pattern.finditer(markdown):
        level = len(match.group(1))
        title = match.group(2).strip()
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        if match.start() < index:
            last_path = [item[1] for item in stack]
        else:
            break
    if last_path:
        return last_path
    return ["Global Context"]


def extract_mermaid_sections(markdown: str) -> List[Tuple[List[str], str]]:
    """
    Extract Mermaid diagrams and their contextual headings from markdown text.

    Returns:
        A list of (heading_path, mermaid_diagram) tuples in the order they appear.
    """
    sections: List[Tuple[List[str], str]] = []
    mermaid_pattern = re.compile(r"```mermaid\s*(.*?)```", flags=re.DOTALL)
    for match in mermaid_pattern.finditer(markdown):
        context_path = _extract_heading_path(markdown, match.start())
        diagram = match.group(1).strip()
        if diagram:
            sections.append((context_path, diagram))
    return sections


MERMAID_TO_CYPHER_PROMPT_TEMPLATE = dedent(
    """
    You are a senior Neo4j and Cypher specialist. Analyze each Mermaid diagram using its
    provided context hierarchy and produce Cypher statements that create the nodes and relationships.

    Requirements:
    - Preserve the intent of the diagram and use meaningful labels/properties.
    - Avoid generic relationship names such as FLOW_TO; choose descriptive relation types drawn from the context.
    - Avoid duplicating nodes; reuse identifiers where appropriate.
    - Group related Cypher statements using comments that reference the context path.
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
    for context_path, diagram in sections:
        context_heading = " > ".join(context_path)
        block = dedent(
            f"""
            # section hierarchy
            {context_heading}
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
