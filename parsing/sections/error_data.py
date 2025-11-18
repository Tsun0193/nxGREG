from __future__ import annotations

import re

from ..context import ParserContext

SECTION_HEADING = "## Error Data Structure"
SECTION_NAME = "Error Data Structure"


def parse_error_data_structure(context: ParserContext) -> None:
    """Parse error handling diagrams and supporting tables."""
    section = context.extract_section(SECTION_HEADING)
    if not section:
        return
    blocks = context.extract_mermaid_blocks(section)
    headings = re.findall(r"###\s+([^\n]+)", section)
    for idx, block in enumerate(blocks):
        heading = headings[idx] if idx < len(headings) else "Error Flow"
        context.add_flow_nodes(
            block=block,
            section_name=heading,
            node_label="ErrorNode",
            relationship_label="ERROR_FLOW",
        )
    tables = context.parse_markdown_tables(section)
    for rows in tables:
        source_key = context.get_source_node(SECTION_NAME, "table", "Error Pattern Table")
        for row in rows:
            error_type = row.get("Error Type")
            if not error_type:
                continue
            node_key = f"error_message:{error_type}"
            context.graph.add_node(
                node_key,
                labels=["ErrorMessagePattern"],
                name=error_type,
                message_pattern=row.get("Message Key Pattern"),
                display_location=row.get("Display Location"),
                section=SECTION_NAME,
            )
            context.graph.add_relationship(
                source_key,
                node_key,
                "FROM_TABLE",
                section=SECTION_NAME,
            )
