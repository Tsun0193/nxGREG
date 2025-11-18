from __future__ import annotations

from ..context import ParserContext

SECTION_HEADING = "## Data Flow Architecture"
SECTION_NAME = "Data Flow"


def parse_data_flow_architecture(context: ParserContext) -> None:
    """Parse the primary data flow Mermaid diagram."""
    section = context.extract_section(SECTION_HEADING)
    if not section:
        return
    blocks = context.extract_mermaid_blocks(section)
    if not blocks:
        return
    context.add_flow_nodes(
        block=blocks[0],
        section_name=SECTION_NAME,
        node_label="DataFlowNode",
        relationship_label="FLOWS_TO",
    )
