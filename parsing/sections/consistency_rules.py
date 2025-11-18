from __future__ import annotations

from ..context import ParserContext

SECTION_HEADING = "## Data Consistency Rules"
SECTION_NAME = "Data Consistency Rules"


def parse_consistency_rules(context: ParserContext) -> None:
    """Parse enumerated consistency constraints from prose."""
    section = context.extract_section(SECTION_HEADING)
    if not section:
        return
    source_key = context.get_source_node(SECTION_NAME, "chunk", "Consistency Rules Text")
    for idx, line in enumerate(section.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("##"):
            continue
        stripped = stripped.lstrip("0123456789. ").strip()
        if not stripped:
            continue
        node_key = f"consistency_rule:{idx}"
        context.graph.add_node(
            node_key,
            labels=["ConsistencyRule"],
            name=stripped,
            section=SECTION_NAME,
            order=str(idx),
        )
        context.graph.add_relationship(
            source_key,
            node_key,
            "FROM_CHUNK",
            section=SECTION_NAME,
        )
