from __future__ import annotations

import re
from typing import Optional, Set

from ..context import ParserContext

SECTION_NAME = "Data Entity Relationships"


def parse_entity_relationships(context: ParserContext) -> None:
    """Parse the main ER diagram block into entity/attribute nodes."""
    block_match = re.search(
        r"```mermaid\s*erDiagram(.*?)```",
        context.document,
        flags=re.DOTALL,
    )
    if not block_match:
        return
    block = block_match.group(1)
    current_entity: Optional[str] = None
    entity_keys: Set[str] = set()
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        rel_match = re.match(
            r"([A-Z0-9_]+)\s+([^\s]+)\s+([A-Z0-9_]+)\s*:\s*\"([^\"]+)\"",
            line,
        )
        if rel_match:
            left, cardinality, right, description = rel_match.groups()
            left_key = f"entity:{left}"
            right_key = f"entity:{right}"
            context.graph.add_node(left_key, labels=["Entity"], name=left, section=SECTION_NAME)
            context.graph.add_node(right_key, labels=["Entity"], name=right, section=SECTION_NAME)
            entity_keys.update([left_key, right_key])
            context.graph.add_relationship(
                left_key,
                right_key,
                "ENTITY_RELATION",
                cardinality=cardinality,
                description=description,
                section=SECTION_NAME,
            )
            continue

        if line.endswith("{"):
            current_entity = line.rstrip("{").strip()
            entity_key = f"entity:{current_entity}"
            context.graph.add_node(
                entity_key,
                labels=["Entity"],
                name=current_entity,
                section=SECTION_NAME,
            )
            entity_keys.add(entity_key)
            continue

        if line == "}" or line.endswith("}"):
            current_entity = None
            continue

        if current_entity:
            if line.startswith("%%"):
                continue
            parts = [part for part in line.split() if part]
            if len(parts) >= 2:
                data_type, field_name, *rest = parts
                constraint = " ".join(rest) if rest else None
                attribute_key = f"attribute:{current_entity}.{field_name}"
                context.graph.add_node(
                    attribute_key,
                    labels=["EntityAttribute"],
                    name=field_name,
                    data_type=data_type,
                    constraint=constraint,
                    entity=current_entity,
                    section=SECTION_NAME,
                )
                context.graph.add_relationship(
                    f"entity:{current_entity}",
                    attribute_key,
                    "HAS_ATTRIBUTE",
                    section=SECTION_NAME,
                )
                entity_keys.add(attribute_key)

    if entity_keys:
        source_key = context.get_source_node(
            SECTION_NAME,
            "graph",
            "Entity Relationship Diagram",
        )
        for key in entity_keys:
            context.graph.add_relationship(
                source_key,
                key,
                "FROM_GRAPH",
                section=SECTION_NAME,
            )
