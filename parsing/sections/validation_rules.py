from __future__ import annotations

import re

from ..context import ParserContext

SECTION_HEADING = "## Data Validation Rules"
SECTION_NAME = "Data Validation Rules"


def parse_validation_rules(context: ParserContext) -> None:
    """Parse validation flow diagrams and tables."""
    section = context.extract_section(SECTION_HEADING)
    if not section:
        return
    blocks = context.extract_mermaid_blocks(section)
    headings = re.findall(
        r"###\s+([^\n]+)",
        section,
    )
    for heading, block in zip(headings, blocks):
        context.add_flow_nodes(
            block=block,
            section_name=heading,
            node_label="ValidationNode",
            relationship_label="VALIDATION_FLOW",
        )
    tables = context.parse_markdown_tables(section)
    for rows in tables:
        source_key = context.get_source_node(SECTION_NAME, "table", "Validation Rules Table")
        for row in rows:
            rule = row.get("Rule") or row.get("Error Type")
            if not rule or rule == "...":
                continue
            node_key = f"validation_rule:{row.get('Rule', row.get('Error Type'))}"
            properties = {
                "rule": row.get("Rule"),
                "condition": row.get("Condition"),
                "error_message": row.get("Error Message"),
                "message_pattern": row.get("Message Key Pattern"),
                "display_location": row.get("Display Location"),
            }
            context.graph.add_node(
                node_key,
                labels=["ValidationRule"],
                section=SECTION_NAME,
                **properties,
            )
            context.graph.add_relationship(
                source_key,
                node_key,
                "FROM_TABLE",
                section=SECTION_NAME,
            )
