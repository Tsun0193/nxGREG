from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from core import GraphData

logger = logging.getLogger(__name__)


@dataclass
class ParserContext:
    """Shared utilities/state used by all section parsers."""

    source_path: Path
    document: str
    graph: GraphData
    _source_nodes: Dict[Tuple[str, str, str], str] = field(default_factory=dict)

    def extract_section(self, heading: str) -> str:
        pattern = re.compile(
            rf"{re.escape(heading)}\s*(.*?)(?=\n## |\Z)",
            flags=re.DOTALL,
        )
        match = pattern.search(self.document)
        return match.group(1).strip() if match else ""

    @staticmethod
    def extract_mermaid_blocks(section_text: str) -> List[str]:
        return re.findall(r"```mermaid\s*(.*?)```", section_text, flags=re.DOTALL)

    @staticmethod
    def parse_markdown_tables(section_text: str) -> List[List[Dict[str, str]]]:
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
                rows.append(dict(zip(headers, columns)))
            if rows:
                tables.append(rows)
        return tables

    def get_source_node(self, section: str, source_type: str, name: str) -> str:
        key = (section, source_type, name)
        cached = self._source_nodes.get(key)
        if cached:
            return cached
        base_slug = _slugify(f"{section}_{name}")
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

    def add_flow_nodes(
        self,
        *,
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
            if not stripped or stripped.startswith(("style", "class", "%%")):
                continue
            participant_match = re.match(
                r"participant\s+([A-Za-z0-9_]+)\s+as\s+(.+)", stripped
            )
            if participant_match:
                node_id, label = participant_match.groups()
                nodes.setdefault(node_id, {})["name"] = label.strip()
                continue
            seq_edge = re.match(
                r"([A-Za-z0-9_]+)\s*-\>+([A-Za-z0-9_]+)\s*:\s*(.+)", stripped
            )
            if seq_edge:
                src, tgt, message = seq_edge.groups()
                source_id, source_label = _parse_node_token(src)
                target_id, target_label = _parse_node_token(tgt)
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
                if len(arrow_split) != 2:
                    continue
                lhs, rhs = arrow_split
                lhs = lhs.strip()
                rhs = rhs.lstrip(">").strip()
                raw_sources = [part.strip() for part in lhs.split("&") if part.strip()]
                sources: List[str] = []
                for raw_source in raw_sources:
                    source_id, source_label = _parse_node_token(raw_source)
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

                target_id, target_label = _parse_node_token(rhs)
                resolved_target = target_id or rhs
                if target_label:
                    nodes.setdefault(resolved_target, {})["name"] = target_label

                edges.append((sources, resolved_target, edge_label, target_note))
                continue

            node_id, label = _parse_node_token(stripped)
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
                rel_type = _normalize_relationship_type(label, relationship_label)
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
            source_node_key = self.get_source_node(section_name, "graph", display_name)
            for node_key in all_node_keys:
                self.graph.add_relationship(
                    source_node_key,
                    node_key,
                    "FROM_GRAPH",
                    section=section_name,
                )


def read_text_with_fallback(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw_bytes = path.read_bytes()
        fallback_encodings = [
            "utf-8-sig",
            "utf-16",
            "utf-16-le",
            "utf-16-be",
            "cp932",
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


def _parse_node_token(token: str) -> Tuple[str, Optional[str]]:
    token = token.strip()
    if not token:
        return "", None
    match = re.match(r"^([A-Za-z0-9_]+)", token)
    if not match:
        return token, None
    node_id = match.group(1)
    remainder = token[match.end():].strip()
    label = _extract_node_label(remainder)
    return node_id, label


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
            if (
                text.startswith(start)
                and text.endswith(end)
                and len(text) >= len(start) + len(end)
            ):
                text = text[len(start) : -len(end)].strip()
                matched = True
                break
        else:
            break
    if not matched:
        return None
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        text = text[1:-1].strip()
    return text or None


def _normalize_relationship_type(raw_label: Optional[str], default: str) -> str:
    candidate = (raw_label or "").strip() or default
    cleaned = re.sub(r"[^0-9A-Za-z]+", "_", candidate).strip("_")
    if not cleaned:
        cleaned = re.sub(r"[^0-9A-Za-z]+", "_", default).strip("_") or "rel"
    if not cleaned[0].isalpha():
        cleaned = f"rel_{cleaned}"
    return cleaned.lower()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_")
    return slug or "item"
