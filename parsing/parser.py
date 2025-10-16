from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

from core import GraphData

logger = logging.getLogger(__name__)


class KnowledgeGraphParser:
    """Parses the README markdown into structured graph data."""

    def __init__(self, readme_path: Path) -> None:
        self.readme_path = readme_path
        self.text = self._read_text_with_fallback(readme_path)
        self.graph = GraphData()
        self._source_nodes: Dict[Tuple[str, str, str], str] = {}

    def parse(self) -> GraphData:
        self._parse_entity_relationships()
        self._parse_data_flow()
        self._parse_processing_patterns()
        self._parse_form_vo_mapping()
        self._parse_validation_flows()
        self._parse_session_management()
        self._parse_error_handling()
        self._parse_consistency_rules()
        return self.graph

    # --------------------------------------------------------------------- utils
    def _extract_section(self, heading: str) -> str:
        pattern = re.compile(
            rf"{re.escape(heading)}\s*(.*?)(?=\n## |\Z)",
            flags=re.DOTALL,
        )
        match = pattern.search(self.text)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _read_text_with_fallback(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_bytes = path.read_bytes()
            fallback_encodings = [
                "utf-8-sig",
                "utf-16",
                "utf-16-le",
                "utf-16-be",
                "cp932",  # common Windows Japanese encoding
                "shift_jis",
                "euc_jp",
                "cp1252",
                "latin-1",
            ]
            for encoding in fallback_encodings:
                try:
                    text = raw_bytes.decode(encoding)
                    logger.warning(
                        "Decoded %s using fallback encoding %s due to UTF-8 decode error.",
                        path,
                        encoding,
                    )
                    return text
                except UnicodeDecodeError:
                    continue
            logger.warning(
                "Failed to decode %s with common fallbacks; using replacement characters.",
                path,
            )
            return raw_bytes.decode("utf-8", errors="replace")

    @staticmethod
    def _extract_mermaid_blocks(section_text: str) -> List[str]:
        return re.findall(r"```mermaid\s*(.*?)```", section_text, flags=re.DOTALL)

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_")
        return slug or "item"

    def _get_source_node(self, section: str, source_type: str, name: str) -> str:
        key = (section, source_type, name)
        cached = self._source_nodes.get(key)
        if cached:
            return cached
        base_slug = self._slugify(f"{section}_{name}")
        node_key = f"source:{source_type}:{base_slug}"
        labels = ["Source", f"{source_type.capitalize()}Source"]
        self.graph.add_node(
            node_key,
            labels=labels,
            name=name,
            data_type=source_type,
            section=section,
        )
        self._source_nodes[key] = node_key
        return node_key

    @staticmethod
    def _parse_markdown_tables(section_text: str) -> List[List[Dict[str, str]]]:
        blocks = re.findall(
            r"(\|[^\n]+\|\n\|[-:| ]+\|\n(?:\|[^\n]*\|\n?)+)",
            section_text,
            flags=re.DOTALL,
        )
        tables: List[List[Dict[str, str]]] = []
        for block in blocks:
            lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
            if len(lines) < 3:
                continue
            headers = [col.strip() for col in lines[0].strip("|").split("|")]
            rows: List[Dict[str, str]] = []
            for line in lines[2:]:
                columns = [col.strip() for col in line.strip("|").split("|")]
                if len(columns) != len(headers):
                    continue
                row = dict(zip(headers, columns))
                rows.append(row)
            if rows:
                tables.append(rows)
        return tables

    @staticmethod
    def _parse_node_token(token: str) -> Tuple[str, Optional[str]]:
        token = token.strip()
        if not token:
            return "", None
        match = re.match(r"^([A-Za-z0-9_]+)", token)
        if not match:
            return token, None
        node_id = match.group(1)
        remainder = token[match.end():].strip()
        label = KnowledgeGraphParser._extract_node_label(remainder)
        return node_id, label

    @staticmethod
    def _extract_node_label(remainder: str) -> Optional[str]:
        if not remainder:
            return None
        text = remainder.strip()
        if not text:
            return None
        if ":::" in text:
            text = text.split(":::", 1)[0].strip()
        shapes = [
            ("[[", "]]"),
            ("((", "))"),
            ("[", "]"),
            ("(", ")"),
            ("{", "}"),
            ("<", ">"),
        ]
        matched = False
        while True:
            for start, end in shapes:
                if text.startswith(start) and text.endswith(end) and len(text) >= len(start) + len(end):
                    text = text[len(start):-len(end)].strip()
                    matched = True
                    break
            else:
                break
        if not matched:
            return None
        if text.startswith('"') and text.endswith('"') and len(text) >= 2:
            text = text[1:-1].strip()
        return text or None

    @staticmethod
    def _normalize_relationship_type(raw_label: Optional[str], default: str) -> str:
        candidate = (raw_label or "").strip()
        if not candidate:
            candidate = default
        cleaned = re.sub(r"[^0-9A-Za-z]+", "_", candidate)
        cleaned = cleaned.strip("_")
        if not cleaned:
            cleaned = re.sub(r"[^0-9A-Za-z]+", "_", default).strip("_") or "rel"
        if not cleaned[0].isalpha():
            cleaned = f"rel_{cleaned}"
        return cleaned.lower()

    def _add_flow_nodes(
        self,
        block: str,
        section_name: str,
        node_label: str,
        relationship_label: str,
        source_name: Optional[str] = None,
    ) -> None:
        nodes: Dict[str, Dict[str, str]] = {}
        edges: List[Tuple[List[str], str, Optional[str], Optional[str]]] = []
        all_node_keys: Set[str] = set()

        for line in block.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("style") or stripped.startswith("class"):
                continue
            if stripped.startswith("%%"):
                continue
            participant_match = re.match(
                r"participant\s+([A-Za-z0-9_]+)\s+as\s+(.+)", stripped
            )
            if participant_match:
                node_id, label = participant_match.groups()
                nodes.setdefault(node_id, {})["name"] = label.strip()
                continue
            seq_edge = re.match(r"([A-Za-z0-9_]+)\s*-\>+([A-Za-z0-9_]+)\s*:\s*(.+)", stripped)
            if seq_edge:
                src, tgt, message = seq_edge.groups()
                source_id, source_label = self._parse_node_token(src)
                target_id, target_label = self._parse_node_token(tgt)
                resolved_source = source_id or src.strip()
                resolved_target = target_id or tgt.strip()
                if source_label:
                    nodes.setdefault(resolved_source, {})["name"] = source_label
                if target_label:
                    nodes.setdefault(resolved_target, {})["name"] = target_label
                edges.append(([resolved_source], resolved_target, message.strip(), None))
                continue
            if "-->" in stripped:
                arrow_split = stripped.split("-->", 1)
                if len(arrow_split) == 2:
                    lhs, rhs = arrow_split
                else:
                    continue
                lhs = lhs.strip()
                rhs = rhs.lstrip(">").strip()
                raw_sources = [part.strip() for part in lhs.split("&") if part.strip()]
                sources: List[str] = []
                for raw_source in raw_sources:
                    source_id, source_label = self._parse_node_token(raw_source)
                    resolved_source = source_id or raw_source
                    sources.append(resolved_source)
                    if source_label:
                        nodes.setdefault(resolved_source, {})["name"] = source_label

                edge_label: Optional[str] = None
                if rhs.startswith("|"):
                    label_split = rhs[1:].split("|", 1)
                    if len(label_split) == 2:
                        edge_label = label_split[0].strip()
                        rhs = label_split[1].strip()

                target_note: Optional[str] = None
                if ":" in rhs:
                    rhs_part, note = rhs.split(":", 1)
                    target_note = note.strip() or None
                    rhs = rhs_part.strip()

                target_id, target_label = self._parse_node_token(rhs)
                resolved_target = target_id or rhs
                if target_label:
                    nodes.setdefault(resolved_target, {})["name"] = target_label

                edges.append((sources, resolved_target, edge_label, target_note))

                continue
            node_id, label = self._parse_node_token(stripped)
            if node_id and label:
                nodes.setdefault(node_id, {})["name"] = label

        for node_id, props in nodes.items():
            node_key = f"{node_label}:{section_name}:{node_id}"
            self.graph.add_node(
                node_key,
                labels=[node_label, "FlowNode"],
                code=node_id,
                name=props.get("name", node_id),
                section=section_name,
            )
            all_node_keys.add(node_key)

        for sources, target, label, note in edges:
            target_key = f"{node_label}:{section_name}:{target}"
            if target_key not in self.graph.nodes:
                self.graph.add_node(
                    target_key,
                    labels=[node_label, "FlowNode"],
                    code=target,
                    name=target,
                    section=section_name,
                )
                all_node_keys.add(target_key)
            for source in sources:
                source_key = f"{node_label}:{section_name}:{source}"
                if source_key not in self.graph.nodes:
                    self.graph.add_node(
                        source_key,
                        labels=[node_label, "FlowNode"],
                        code=source,
                        name=source,
                        section=section_name,
                    )
                    all_node_keys.add(source_key)
                rel_type = self._normalize_relationship_type(label, relationship_label)
                self.graph.add_relationship(
                    source_key,
                    target_key,
                    rel_type,
                    label=label,
                    note=note,
                    section=section_name,
                    category=relationship_label,
                )

        if all_node_keys:
            display_name = source_name or f"{section_name} Diagram"
            source_node_key = self._get_source_node(section_name, "graph", display_name)
            for node_key in all_node_keys:
                self.graph.add_relationship(
                    source_node_key,
                    node_key,
                    "FROM_GRAPH",
                    section=section_name,
                )

    # ------------------------------------------------------------- section parsers
    def _parse_entity_relationships(self) -> None:
        block_match = re.search(
            r"```mermaid\s*erDiagram(.*?)```",
            self.text,
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
                self.graph.add_node(left_key, labels=["Entity"], name=left, section="Data Entity Relationships")
                self.graph.add_node(right_key, labels=["Entity"], name=right, section="Data Entity Relationships")
                entity_keys.update([left_key, right_key])
                self.graph.add_relationship(
                    left_key,
                    right_key,
                    "ENTITY_RELATION",
                    cardinality=cardinality,
                    description=description,
                    section="Data Entity Relationships",
                )
                continue

            if line.endswith("{"):
                current_entity = line.rstrip("{").strip()
                entity_key = f"entity:{current_entity}"
                self.graph.add_node(
                    entity_key,
                    labels=["Entity"],
                    name=current_entity,
                    section="Data Entity Relationships",
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
                    self.graph.add_node(
                        attribute_key,
                        labels=["EntityAttribute"],
                        name=field_name,
                        data_type=data_type,
                        constraint=constraint,
                        entity=current_entity,
                        section="Data Entity Relationships",
                    )
                    self.graph.add_relationship(
                        f"entity:{current_entity}",
                        attribute_key,
                        "HAS_ATTRIBUTE",
                        section="Data Entity Relationships",
                    )
                    entity_keys.add(attribute_key)

        if entity_keys:
            source_key = self._get_source_node(
                "Data Entity Relationships",
                "graph",
                "Entity Relationship Diagram",
            )
            for key in entity_keys:
                self.graph.add_relationship(
                    source_key,
                    key,
                    "FROM_GRAPH",
                    section="Data Entity Relationships",
                )

    def _parse_data_flow(self) -> None:
        section = self._extract_section("## Data Flow Architecture")
        if not section:
            return
        blocks = self._extract_mermaid_blocks(section)
        if not blocks:
            return
        block = blocks[0]
        self._add_flow_nodes(
            block=block,
            section_name="Data Flow",
            node_label="DataFlowNode",
            relationship_label="FLOWS_TO",
        )

    def _parse_processing_patterns(self) -> None:
        section = self._extract_section("## Data Processing Patterns")
        if not section:
            return
        blocks = self._extract_mermaid_blocks(section)
        headings = re.findall(r"###\s+([^\n]+)", section)
        for idx, block in enumerate(blocks):
            heading = headings[idx] if idx < len(headings) else f"Pattern {idx+1}"
            node_label = "ProcessNode"
            rel_label = "PROCESS_FLOW"
            self._add_flow_nodes(
                block=block,
                section_name=heading,
                node_label=node_label,
                relationship_label=rel_label,
            )

    def _parse_form_vo_mapping(self) -> None:
        section = self._extract_section("## Form to VO Mapping")
        if not section:
            return
        form_sections = re.findall(
            r"###\s+([^\n]+)\n(.*?)(?=\n### |\Z)",
            section,
            flags=re.DOTALL,
        )
        for heading, body in form_sections:
            form_names = []
            title_match = re.search(r"\(([^)]+)\)", heading)
            if title_match:
                form_names = [name.strip() for name in title_match.group(1).split(",")]
            form_group = heading.split("(")[0].strip()
            for form_name in form_names:
                form_key = f"form:{form_name}"
                self.graph.add_node(
                    form_key,
                    labels=["Form"],
                    name=form_name,
                    description=form_group,
                    section="Form to VO Mapping",
                )
            tables = self._parse_markdown_tables(body)
            if not tables:
                continue
            for table_idx, rows in enumerate(tables, start=1):
                table_name = f"{form_group} Table {table_idx}" if len(tables) > 1 else f"{form_group} Table"
                source_key = self._get_source_node("Form to VO Mapping", "table", table_name)
                for row in rows:
                    form_field = row.get("Form Field")
                    vo_property = row.get("VO Property")
                    data_type = row.get("Data Type")
                    purpose = row.get("Purpose")
                    if not form_field or form_field == "...":
                        continue
                    field_key = f"formfield:{form_group}:{form_field}"
                    self.graph.add_node(
                        field_key,
                        labels=["FormField"],
                        name=form_field,
                        data_type=data_type,
                        purpose=purpose,
                        section="Form to VO Mapping",
                        form_group=form_group,
                    )
                    self.graph.add_relationship(
                        source_key,
                        field_key,
                        "FROM_TABLE",
                        section="Form to VO Mapping",
                    )
                    for form_name in form_names:
                        self.graph.add_relationship(
                            f"form:{form_name}",
                            field_key,
                            "HAS_FIELD",
                            section="Form to VO Mapping",
                        )
                    if vo_property and vo_property != "...":
                        vo_key = f"vo_property:{vo_property}"
                        self.graph.add_node(
                            vo_key,
                            labels=["VOProperty"],
                            name=vo_property,
                            section="Form to VO Mapping",
                        )
                        self.graph.add_relationship(
                            field_key,
                            vo_key,
                            "BINDS_TO",
                            section="Form to VO Mapping",
                        )
                        self.graph.add_relationship(
                            source_key,
                            vo_key,
                            "FROM_TABLE",
                            section="Form to VO Mapping",
                        )

    def _parse_validation_flows(self) -> None:
        section = self._extract_section("## Data Validation Rules")
        if not section:
            return
        blocks = self._extract_mermaid_blocks(section)
        headings = re.findall(
            r"###\s+([^\n]+)",
            section,
        )
        for heading, block in zip(headings, blocks):
            self._add_flow_nodes(
                block=block,
                section_name=heading,
                node_label="ValidationNode",
                relationship_label="VALIDATION_FLOW",
            )
        tables = self._parse_markdown_tables(section)
        for rows in tables:
            source_key = self._get_source_node("Data Validation Rules", "table", "Validation Rules Table")
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
                self.graph.add_node(
                    node_key,
                    labels=["ValidationRule"],
                    section="Data Validation Rules",
                    **properties,
                )
                self.graph.add_relationship(
                    source_key,
                    node_key,
                    "FROM_TABLE",
                    section="Data Validation Rules",
                )

    def _parse_session_management(self) -> None:
        section = self._extract_section("## Session Data Management")
        if not section:
            return
        tables = self._parse_markdown_tables(section)
        for idx, rows in enumerate(tables, start=1):
            table_name = "Session Data Table" if len(tables) == 1 else f"Session Data Table {idx}"
            source_key = self._get_source_node("Session Data Management", "table", table_name)
            for row in rows:
                key_name = row.get("Session Key")
                if not key_name or key_name == "...":
                    continue
                node_key = f"session_key:{key_name}"
                self.graph.add_node(
                    node_key,
                    labels=["SessionKey"],
                    name=key_name,
                    data_type=row.get("Data Type"),
                    purpose=row.get("Purpose"),
                    section="Session Data Management",
                )
                self.graph.add_relationship(
                    source_key,
                    node_key,
                    "FROM_TABLE",
                    section="Session Data Management",
                )
                data_type = row.get("Data Type")
                if data_type and data_type not in {"...", ""}:
                    vo_key = f"vo:{data_type}"
                    self.graph.add_node(
                        vo_key,
                        labels=["VO"],
                        name=data_type,
                        section="Session Data Management",
                    )
                    self.graph.add_relationship(
                        node_key,
                        vo_key,
                        "STORES",
                        section="Session Data Management",
                    )
                    self.graph.add_relationship(
                        source_key,
                        vo_key,
                        "FROM_TABLE",
                        section="Session Data Management",
                    )
        blocks = self._extract_mermaid_blocks(section)
        if blocks:
            self._add_flow_nodes(
                block=blocks[-1],
                section_name="Session Lifecycle",
                node_label="SessionNode",
                relationship_label="SESSION_FLOW",
            )

    def _parse_error_handling(self) -> None:
        section = self._extract_section("## Error Data Structure")
        if not section:
            return
        blocks = self._extract_mermaid_blocks(section)
        headings = re.findall(r"###\s+([^\n]+)", section)
        for idx, block in enumerate(blocks):
            heading = headings[idx] if idx < len(headings) else "Error Flow"
            node_label = "ErrorNode" if "Pattern" in heading else "ErrorNode"
            rel_label = "ERROR_FLOW"
            self._add_flow_nodes(
                block=block,
                section_name=heading,
                node_label=node_label,
                relationship_label=rel_label,
            )
        tables = self._parse_markdown_tables(section)
        for rows in tables:
            source_key = self._get_source_node("Error Data Structure", "table", "Error Pattern Table")
            for row in rows:
                error_type = row.get("Error Type")
                if not error_type:
                    continue
                node_key = f"error_message:{error_type}"
                self.graph.add_node(
                    node_key,
                    labels=["ErrorMessagePattern"],
                    name=error_type,
                    message_pattern=row.get("Message Key Pattern"),
                    display_location=row.get("Display Location"),
                    section="Error Data Structure",
                )
                self.graph.add_relationship(
                    source_key,
                    node_key,
                    "FROM_TABLE",
                    section="Error Data Structure",
                )

    def _parse_consistency_rules(self) -> None:
        section = self._extract_section("## Data Consistency Rules")
        if not section:
            return
        source_key = self._get_source_node("Data Consistency Rules", "chunk", "Consistency Rules Text")
        for idx, line in enumerate(section.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("##"):
                continue
            stripped = stripped.lstrip("0123456789. ").strip()
            if not stripped:
                continue
            node_key = f"consistency_rule:{idx}"
            self.graph.add_node(
                node_key,
                labels=["ConsistencyRule"],
                name=stripped,
                section="Data Consistency Rules",
                order=str(idx),
            )
            self.graph.add_relationship(
                source_key,
                node_key,
                "FROM_CHUNK",
                section="Data Consistency Rules",
            )
