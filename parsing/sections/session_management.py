from __future__ import annotations

from ..context import ParserContext

SECTION_HEADING = "## Session Data Management"
SECTION_NAME = "Session Data Management"
LIFECYCLE_SECTION = "Session Lifecycle"


def parse_session_data_management(context: ParserContext) -> None:
    """Parse session storage tables and lifecycle diagrams."""
    section = context.extract_section(SECTION_HEADING)
    if not section:
        return
    tables = context.parse_markdown_tables(section)
    for idx, rows in enumerate(tables, start=1):
        table_name = "Session Data Table" if len(tables) == 1 else f"Session Data Table {idx}"
        source_key = context.get_source_node(SECTION_NAME, "table", table_name)
        for row in rows:
            key_name = row.get("Session Key")
            if not key_name or key_name == "...":
                continue
            node_key = f"session_key:{key_name}"
            context.graph.add_node(
                node_key,
                labels=["SessionKey"],
                name=key_name,
                data_type=row.get("Data Type"),
                purpose=row.get("Purpose"),
                section=SECTION_NAME,
            )
            context.graph.add_relationship(
                source_key,
                node_key,
                "FROM_TABLE",
                section=SECTION_NAME,
            )
            data_type = row.get("Data Type")
            if data_type and data_type not in {"...", ""}:
                vo_key = f"vo:{data_type}"
                context.graph.add_node(
                    vo_key,
                    labels=["VO"],
                    name=data_type,
                    section=SECTION_NAME,
                )
                context.graph.add_relationship(
                    node_key,
                    vo_key,
                    "STORES",
                    section=SECTION_NAME,
                )
                context.graph.add_relationship(
                    source_key,
                    vo_key,
                    "FROM_TABLE",
                    section=SECTION_NAME,
                )
    blocks = context.extract_mermaid_blocks(section)
    if blocks:
        context.add_flow_nodes(
            block=blocks[-1],
            section_name=LIFECYCLE_SECTION,
            node_label="SessionNode",
            relationship_label="SESSION_FLOW",
        )
