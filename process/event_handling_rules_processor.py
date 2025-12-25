from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class _Section:
    level: int
    title_raw: str
    content: str


class EventHandlingRulesProcessor:
    """Parse event handling rules markdown into graph entities + relationships.

    Target file (by default):
      ctc-data-en/<module>/<basic_tab>/screen-specification/event_handling_rules-en.md

    Output format mirrors other processors in `process/`:
      {
        "module": ...,
        "tab_name": ...,
        "source_file": ...,
        "entities": [...],
        "relationships": [...],
      }
    """

    def __init__(
        self,
        base_path: str | Path,
        module_name: str = "simple",
        basic_tab_name: Optional[str] = None,
        file_path: Optional[str | Path] = None,
        include_table_level_entities: bool = False,
        include_event_row_entities: bool = False,
    ) -> None:
        self.base_path = Path(base_path)
        self.module_name = module_name

        if basic_tab_name is None:
            if module_name == "simple":
                self.basic_tab_name = "yuusyou-kihon"
            elif module_name == "housing":
                self.basic_tab_name = "basic-info-housing-contract"
            elif module_name == "contract-list":
                self.basic_tab_name = "contract-list"  # No actual tab, just for consistency
            else:
                self.basic_tab_name = "unknown"
        else:
            self.basic_tab_name = basic_tab_name

        if file_path is None:
            if module_name == "contract-list":
                # contract-list has no tab folder, goes directly to screen-specification
                self.file_path = (
                    self.base_path
                    / self.module_name
                    / "screen-specification"
                    / "event_handling_rules-en.md"
                )
            else:
                # simple and housing have tab folders
                self.file_path = (
                    self.base_path
                    / self.module_name
                    / self.basic_tab_name
                    / "screen-specification"
                    / "event_handling_rules-en.md"
                )
        else:
            self.file_path = Path(file_path)

        # When True, emit table-derived entities like event groups and flow mappings.
        # Default False for now to keep the graph coarser-grained.
        self.include_table_level_entities = include_table_level_entities

        # When True, emit one entity per table row (type: "event") and its relationships.
        # Kept behind a separate flag.
        self.include_event_row_entities = include_event_row_entities

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"`", "", text)
        text = re.sub(r"\([^\)]*\)", "", text)  # drop parenthetical hints
        text = re.sub(r"[^a-z0-9_\-\s]", "", text)
        text = re.sub(r"[\s\-]+", "_", text)
        return text.strip("_") or "section"

    @staticmethod
    def _strip_heading_number(title: str) -> Tuple[Optional[str], str]:
        raw = title.strip()

        # "1. Title" or "2.1. Title"
        m = re.match(r"^(\d+(?:\.\d+)*)\.\s+(.+?)\s*$", raw)
        if m:
            return m.group(1), m.group(2).strip()

        # "2.1 Title" style
        m = re.match(r"^(\d+(?:\.\d+)+)\s+(.+?)\s*$", raw)
        if m:
            return m.group(1), m.group(2).strip()

        return None, raw

    @staticmethod
    def _parse_sections(markdown: str) -> Tuple[str, List[_Section]]:
        doc_title = ""
        title_match = re.search(r"^#\s+(.+?)\s*$", markdown, flags=re.MULTILINE)
        if title_match:
            doc_title = title_match.group(1).strip()

        heading_re = re.compile(r"^(#{2,6})\s+(.+?)\s*$", flags=re.MULTILINE)
        matches = list(heading_re.finditer(markdown))

        sections: List[_Section] = []
        for i, m in enumerate(matches):
            level = len(m.group(1))
            title_raw = m.group(2).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            content = markdown[start:end].strip("\n")
            sections.append(_Section(level=level, title_raw=title_raw, content=content.strip()))

        return doc_title, sections

    @staticmethod
    def _extract_backticked_values(text: str) -> List[str]:
        return [m.group(1).strip() for m in re.finditer(r"`([^`]+?)`", text)]

    @staticmethod
    def _parse_markdown_table(table_block: str) -> List[Dict[str, str]]:
        """Parse a simple pipe-delimited markdown table into row dicts.

        Supports the typical format:
          | H1 | H2 |
          |----|----|
          | v1 | v2 |

        Returns [] if no valid table is detected.
        """
        lines = [ln.strip() for ln in table_block.splitlines() if ln.strip()]
        if len(lines) < 2:
            return []

        # Find header line (first line starting with |)
        header_idx = next((i for i, ln in enumerate(lines) if ln.startswith("|") and ln.endswith("|")), None)
        if header_idx is None or header_idx + 1 >= len(lines):
            return []

        header_line = lines[header_idx]
        sep_line = lines[header_idx + 1]

        # Separator must be like |---|---|
        if not re.match(r"^\|\s*[-: ]+\|(?:\s*[-: ]+\|)+\s*$", sep_line):
            return []

        headers = [h.strip() for h in header_line.strip("|").split("|")]
        headers = [h for h in headers if h]
        if not headers:
            return []

        rows: List[Dict[str, str]] = []
        for ln in lines[header_idx + 2 :]:
            if not (ln.startswith("|") and ln.endswith("|")):
                break
            parts = [p.strip() for p in ln.strip("|").split("|")]
            # Pad/truncate to headers length
            if len(parts) < len(headers):
                parts = parts + [""] * (len(headers) - len(parts))
            elif len(parts) > len(headers):
                parts = parts[: len(headers)]

            row = {headers[i]: parts[i] for i in range(len(headers))}
            # Skip placeholder rows
            no_val = row.get("No.") or row.get("No") or ""
            if row.get(headers[0], "").strip() in {"", "..."} and no_val.strip() in {"", "..."}:
                continue
            rows.append(row)

        return rows

    @staticmethod
    def _find_first_table_block(text: str) -> Optional[str]:
        """Return the first markdown table block in text, if any."""
        # Heuristic: find a header line with pipes, then separator line, then rows.
        table_re = re.compile(
            r"(\|[^\n]+\|\n\|[-: \|]+\|\n(?:\|[^\n]+\|\n)+)", re.MULTILINE
        )
        m = table_re.search(text)
        return m.group(1) if m else None

    @staticmethod
    def _extract_mermaid_blocks(text: str) -> List[str]:
        return [m.group(1).strip() for m in re.finditer(r"```mermaid\s*\n(.*?)```", text, re.DOTALL)]

    @staticmethod
    def _guess_mermaid_kind(mermaid_code: str) -> str:
        first = mermaid_code.strip().splitlines()[0].strip() if mermaid_code.strip() else ""
        if first.startswith("sequenceDiagram"):
            return "sequenceDiagram"
        if first.startswith("flowchart"):
            return "flowchart"
        return "mermaid"

    @staticmethod
    def _normalize_event_type_from_heading(clean_title: str) -> str:
        t = clean_title.lower()
        if "crud" in t:
            return "CRUD"
        if "search" in t:
            return "Search"
        if "print" in t:
            return "Print"
        if "navigation" in t:
            return "Navigation"
        return clean_title

    def _current_tab_entity_id(self) -> Optional[str]:
        """Return the graph entity id for the tab/module this rules doc belongs to.

        In this dataset, the file lives under the module's *basic information* tab folder,
        except for contract-list which has no tab folder:
        - simple/yuusyou-kihon -> tab:basic_information
        - housing/basic-info-housing-contract -> tab:basic_information_housing
        - contract-list -> module:contract_list (no basic tab)
        """
        if self.module_name == "simple" and self.basic_tab_name == "yuusyou-kihon":
            return "tab:basic_information"
        if self.module_name == "housing" and self.basic_tab_name == "basic-info-housing-contract":
            return "tab:basic_information_housing"
        if self.module_name == "contract-list":
            return "module:contract-list"
        return None

    def process(self) -> Dict[str, Any]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Event handling rules file not found: {self.file_path}")

        markdown = self.file_path.read_text(encoding="utf-8")
        doc_title, sections = self._parse_sections(markdown)

        source_file = str(self.file_path.relative_to(self.base_path)).replace("\\", "/")

        if self.module_name == "contract-list":
            root_id = f"event_processing_rules:{self.module_name}"
        else:
            root_id = f"event_processing_rules:{self.module_name}:{self.basic_tab_name}"
        root_name = doc_title or "Event Processing Rules"

        entities: List[Dict[str, Any]] = [
            {
                "id": root_id,
                "type": "event_processing_rules",
                "name": root_name,
                "module": self.module_name,
                "tab_name": self.basic_tab_name,
                "source_file": source_file,
            }
        ]

        relationships: List[Dict[str, Any]] = []

        current_tab_id = self._current_tab_entity_id()
        if current_tab_id:
            relationships.append(
                {
                    "source": root_id,
                    "target": current_tab_id,
                    "relationship_type": "DESCRIBES",
                    "description": f"Event processing rules describe {current_tab_id}",
                }
            )

        # 1) Always create heading-based section entities for traceability
        stack: List[Tuple[int, str]] = []  # (heading_level, entity_id)
        slug_counts: Dict[str, int] = {}
        section_id_by_key: Dict[Tuple[int, str], str] = {}

        for section in sections:
            _, clean_title = self._strip_heading_number(section.title_raw)
            base_slug = self._slugify(clean_title)
            slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1
            slug = base_slug if slug_counts[base_slug] == 1 else f"{base_slug}_{slug_counts[base_slug]}"

            if self.module_name == "contract-list":
                section_id = f"event_processing_rules_section:{self.module_name}:{slug}"
            else:
                section_id = f"event_processing_rules_section:{self.module_name}:{self.basic_tab_name}:{slug}"
            entities.append(
                {
                    "id": section_id,
                    "type": "event_processing_rules_section",
                    "name": clean_title,
                    "module": self.module_name,
                    "tab_name": self.basic_tab_name,
                    "source_file": source_file,
                    "heading_level": section.level,
                    "heading_raw": section.title_raw,
                    "content": section.content,
                }
            )

            while stack and stack[-1][0] >= section.level:
                stack.pop()
            parent_id = stack[-1][1] if stack else root_id
            relationships.append(
                {"source": parent_id, "target": section_id, "relationship_type": "HAS_SECTION"}
            )

            stack.append((section.level, section_id))
            section_id_by_key[(section.level, section.title_raw)] = section_id

        # 2) Extract event tables from level-3 sections under "Main Events List"
        event_groups: Dict[str, str] = {}  # event_type -> group_entity_id

        for section in sections:
            if section.level != 3:
                continue

            _, clean_title = self._strip_heading_number(section.title_raw)
            event_type = self._normalize_event_type_from_heading(clean_title)

            table_block = self._find_first_table_block(section.content)
            if not table_block:
                continue

            rows = self._parse_markdown_table(table_block)
            # The main events tables have a "JavaScript Function" header.
            if not rows or not any("JavaScript" in h for h in (rows[0].keys() if rows else [])):
                continue

            group_slug = self._slugify(event_type)
            if self.module_name == "contract-list":
                group_id = f"event_group:{self.module_name}:{group_slug}"
            else:
                group_id = f"event_group:{self.module_name}:{self.basic_tab_name}:{group_slug}"
            if self.include_table_level_entities:
                if group_id not in event_groups.values():
                    event_groups[event_type] = group_id
                    entities.append(
                        {
                            "id": group_id,
                            "type": "event_group",
                            "name": event_type,
                            "module": self.module_name,
                            "tab_name": self.basic_tab_name,
                            "source_file": source_file,
                        }
                    )
                    relationships.append(
                        {"source": root_id, "target": group_id, "relationship_type": "HAS_EVENT_GROUP"}
                    )

                # Link the heading section -> group (optional but helpful)
                section_entity_id = section_id_by_key.get((section.level, section.title_raw))
                if section_entity_id:
                    relationships.append(
                        {"source": section_entity_id, "target": group_id, "relationship_type": "DESCRIBES"}
                    )

            if self.include_table_level_entities and self.include_event_row_entities:
                for row in rows:
                    no = (row.get("No.") or row.get("No") or "").strip()
                    button = (row.get("Button") or "").strip()
                    js_func_raw = (row.get("JavaScript Function") or "").strip()
                    action_type = (row.get("Action Type") or "").strip()
                    description = (row.get("Description") or "").strip()

                    # Unwrap single backticks around some cells
                    js_funcs = (
                        self._extract_backticked_values(js_func_raw) or [js_func_raw] if js_func_raw else []
                    )
                    action_types = (
                        self._extract_backticked_values(action_type) or [action_type] if action_type else []
                    )

                    # Prefer a stable id component
                    action_key = action_types[0] if action_types and action_types[0] else action_type
                    action_key = action_key.strip() or button or f"row_{no or 'x'}"
                    if self.module_name == "contract-list":
                        event_id = (
                            f"event:{self.module_name}:{group_slug}:"
                            f"{self._slugify(action_key)}:{no or 'x'}"
                        )
                    else:
                        event_id = (
                            f"event:{self.module_name}:{self.basic_tab_name}:{group_slug}:"
                            f"{self._slugify(action_key)}:{no or 'x'}"
                        )

                    entities.append(
                        {
                            "id": event_id,
                            "type": "event",
                            "name": f"{event_type} - {button}" if button else f"{event_type} Event",
                            "module": self.module_name,
                            "tab_name": self.basic_tab_name,
                            "source_file": source_file,
                            "event_type": event_type,
                            "row_no": no,
                            "button": button,
                            "javascript_function_raw": js_func_raw,
                            "javascript_functions": js_funcs,
                            "action_type_raw": action_type,
                            "action_types": action_types,
                            "description": description,
                        }
                    )

                    relationships.append(
                        {"source": group_id, "target": event_id, "relationship_type": "CONTAINS_EVENT"}
                    )
                    relationships.append(
                        {"source": root_id, "target": event_id, "relationship_type": "HAS_EVENT"}
                    )

        # 3) Extract mermaid flows from any sections
        for section in sections:
            mermaid_blocks = self._extract_mermaid_blocks(section.content)
            if not mermaid_blocks:
                continue

            _, clean_title = self._strip_heading_number(section.title_raw)
            for idx, code in enumerate(mermaid_blocks, start=1):
                kind = self._guess_mermaid_kind(code)
                slug = self._slugify(clean_title)
                if self.module_name == "contract-list":
                    flow_id = f"event_flow:{self.module_name}:{slug}:{idx}"
                else:
                    flow_id = f"event_flow:{self.module_name}:{self.basic_tab_name}:{slug}:{idx}"
                entities.append(
                    {
                        "id": flow_id,
                        "type": "event_processing_flow",
                        "name": clean_title,
                        "module": self.module_name,
                        "tab_name": self.basic_tab_name,
                        "source_file": source_file,
                        "mermaid_kind": kind,
                        "mermaid": code,
                    }
                )
                relationships.append(
                    {"source": root_id, "target": flow_id, "relationship_type": "HAS_FLOW"}
                )

                section_entity_id = section_id_by_key.get((section.level, section.title_raw))
                if section_entity_id:
                    relationships.append(
                        {"source": section_entity_id, "target": flow_id, "relationship_type": "HAS_DIAGRAM"}
                    )

        # 4) Extract event flow mapping table (section 3)
        mapping_rows: List[Dict[str, str]] = []
        for section in sections:
            # Find the section likely titled "Event Flow Mapping"
            _, clean_title = self._strip_heading_number(section.title_raw)
            if section.level in {2, 3} and "event flow mapping" in clean_title.lower():
                table_block = self._find_first_table_block(section.content)
                if table_block:
                    mapping_rows = self._parse_markdown_table(table_block)
                break

        mapping_by_type: Dict[str, str] = {}
        if self.include_table_level_entities:
            for row in mapping_rows:
                event_type = (row.get("Event Type") or "").strip()
                trigger = (row.get("Trigger") or "").strip()
                process = (row.get("Process") or "").strip()
                result = (row.get("Result") or "").strip()

                if not event_type:
                    continue

                if self.module_name == "contract-list":
                    mapping_id = f"event_flow_mapping:{self.module_name}:{self._slugify(event_type)}"
                else:
                    mapping_id = (
                        f"event_flow_mapping:{self.module_name}:{self.basic_tab_name}:{self._slugify(event_type)}"
                    )
                mapping_by_type[event_type] = mapping_id

                entities.append(
                    {
                        "id": mapping_id,
                        "type": "event_flow_mapping",
                        "name": event_type,
                        "module": self.module_name,
                        "tab_name": self.basic_tab_name,
                        "source_file": source_file,
                        "trigger": trigger,
                        "process": process,
                        "result": result,
                    }
                )
                relationships.append(
                    {"source": root_id, "target": mapping_id, "relationship_type": "HAS_MAPPING"}
                )

            # Link groups -> mappings where possible
            for event_type, group_id in event_groups.items():
                # Match against mapping rows by normalized label
                mapping_id = mapping_by_type.get(event_type)
                if not mapping_id:
                    # Try a best-effort mapping (e.g., group "Search" might match "Search")
                    mapping_id = mapping_by_type.get(self._normalize_event_type_from_heading(event_type))
                if mapping_id:
                    relationships.append(
                        {"source": group_id, "target": mapping_id, "relationship_type": "FOLLOWS_MAPPING"}
                    )

        return {
            "module": self.module_name,
            "tab_name": self.basic_tab_name,
            "source_file": source_file,
            "entities": entities,
            "relationships": relationships,
        }

    def save_to_json(self, output_path: str | Path) -> None:
        results = self.process()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


def main() -> None:
    
    base_path = "/data_hdd_16t/vuongchu/nxGREG/ctc-data-en"
    modules = ["housing", "simple", "contract-list"]
    
    for module in modules:
        output_path = f"/data_hdd_16t/vuongchu/nxGREG/json/{module}/{module}-event-rules.json"
        
        # contract-list has no basic tab, so basic_tab_name will be auto-set in __init__
        processor = EventHandlingRulesProcessor(base_path, module_name=module)
        processor.save_to_json(output_path)
    
    print("Event handling rules JSON files generated successfully!")
    




if __name__ == "__main__":
    main()
