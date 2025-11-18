from __future__ import annotations

import re

from ..context import ParserContext

SECTION_HEADING = "## Data Processing Patterns"


def parse_processing_patterns(context: ParserContext) -> None:
    """Parse each processing pattern Mermaid diagram."""
    section = context.extract_section(SECTION_HEADING)
    if not section:
        return
    blocks = context.extract_mermaid_blocks(section)
    headings = re.findall(r"###\s+([^\n]+)", section)
    for idx, block in enumerate(blocks):
        heading = headings[idx] if idx < len(headings) else f"Pattern {idx + 1}"
        context.add_flow_nodes(
            block=block,
            section_name=heading,
            node_label="ProcessNode",
            relationship_label="PROCESS_FLOW",
        )
