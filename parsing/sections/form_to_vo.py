from __future__ import annotations

import re
from typing import List

from ..context import ParserContext

SECTION_HEADING = "## Form to VO Mapping"
SECTION_NAME = "Form to VO Mapping"


def parse_form_to_vo_mapping(context: ParserContext) -> None:
    """Parse form groups, form fields, and their VO bindings."""
    section = context.extract_section(SECTION_HEADING)
    if not section:
        return
    form_sections = re.findall(
        r"###\s+([^\n]+)\n(.*?)(?=\n### |\Z)",
        section,
        flags=re.DOTALL,
    )
    for heading, body in form_sections:
        form_names: List[str] = []
        title_match = re.search(r"\(([^)]+)\)", heading)
        if title_match:
            form_names = [name.strip() for name in title_match.group(1).split(",")]
        form_group = heading.split("(")[0].strip()
        for form_name in form_names:
            form_key = f"form:{form_name}"
            context.graph.add_node(
                form_key,
                labels=["Form"],
                name=form_name,
                description=form_group,
                section=SECTION_NAME,
            )
        tables = context.parse_markdown_tables(body)
        if not tables:
            continue
        for table_idx, rows in enumerate(tables, start=1):
            table_name = (
                f"{form_group} Table {table_idx}" if len(tables) > 1 else f"{form_group} Table"
            )
            source_key = context.get_source_node(SECTION_NAME, "table", table_name)
            for row in rows:
                form_field = row.get("Form Field")
                vo_property = row.get("VO Property")
                data_type = row.get("Data Type")
                purpose = row.get("Purpose")
                if not form_field or form_field == "...":
                    continue
                field_key = f"formfield:{form_group}:{form_field}"
                context.graph.add_node(
                    field_key,
                    labels=["FormField"],
                    name=form_field,
                    data_type=data_type,
                    purpose=purpose,
                    section=SECTION_NAME,
                    form_group=form_group,
                )
                context.graph.add_relationship(
                    source_key,
                    field_key,
                    "FROM_TABLE",
                    section=SECTION_NAME,
                )
                for form_name in form_names:
                    context.graph.add_relationship(
                        f"form:{form_name}",
                        field_key,
                        "HAS_FIELD",
                        section=SECTION_NAME,
                    )
                if vo_property and vo_property != "...":
                    vo_key = f"vo_property:{vo_property}"
                    context.graph.add_node(
                        vo_key,
                        labels=["VOProperty"],
                        name=vo_property,
                        section=SECTION_NAME,
                    )
                    context.graph.add_relationship(
                        field_key,
                        vo_key,
                        "BINDS_TO",
                        section=SECTION_NAME,
                    )
                    context.graph.add_relationship(
                        source_key,
                        vo_key,
                        "FROM_TABLE",
                        section=SECTION_NAME,
                    )
