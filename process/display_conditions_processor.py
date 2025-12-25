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


class DisplayConditionsProcessor:
    """Parse display conditions markdown into graph entities + relationships.

    Target files:
      ctc-data-en/<module>/<tab>/screen-specification/display_conditions-en.md
      ctc-data-en/contract-list/screen-specification/display-conditions-en.md

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
        tab_name: Optional[str] = None,
        file_path: Optional[str | Path] = None,
    ) -> None:
        self.base_path = Path(base_path)
        self.module_name = module_name

        # Determine tab name based on module
        if tab_name is None:
            if module_name == "simple":
                self.tab_name = "yuusyou-kihon"
            elif module_name == "housing":
                self.tab_name = "basic-info-housing-contract"
            elif module_name == "contract-list":
                self.tab_name = "contract-list"
            else:
                self.tab_name = "unknown"
        else:
            self.tab_name = tab_name

        # Determine file path
        if file_path is None:
            if module_name == "contract-list":
                # contract-list has no tab folder, goes directly to screen-specification
                self.file_path = (
                    self.base_path
                    / self.module_name
                    / "screen-specification"
                    / "display-conditions-en.md"
                )
            else:
                # simple and housing have tab folders
                self.file_path = (
                    self.base_path
                    / self.module_name
                    / self.tab_name
                    / "screen-specification"
                    / "display_conditions-en.md"
                )
        else:
            self.file_path = Path(file_path)

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
        """Return (section_number, clean_title)."""
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
        """Parse markdown into (document_title, sections).

        Sections are created for headings level 2+ ("##", "###", ...).
        Each section's `content` is the body until the next heading of level 2+.
        """
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
    def _extract_screen_metadata(markdown: str) -> Dict[str, str]:
        """Extract screen metadata from after the h1 title.

        Expected format (after # heading, before ## heading):
        **Target Screen:** ...
        **Main JSP:** ...
        **Body JSP:** ...
        **Primary Action:** ...
        **Form Bean:** ...
        
        Returns normalized snake_case keys.
        """
        metadata: Dict[str, str] = {}
        
        # Find content between h1 title and first h2 heading
        # First, find the h1 title
        h1_match = re.search(r"^#\s+.+$", markdown, flags=re.MULTILINE)
        if not h1_match:
            return metadata
        
        # Start after the h1 title
        start_pos = h1_match.end()
        
        # Find the first h2+ heading
        h2_match = re.search(r"^#{2,6}\s+", markdown[start_pos:], flags=re.MULTILINE)
        
        # Extract the header section
        if h2_match:
            header_section = markdown[start_pos:start_pos + h2_match.start()]
        else:
            header_section = markdown[start_pos:]

        # Extract key-value pairs by processing each line
        for line in header_section.splitlines():
            line = line.strip()
            # Match pattern: **Key:** value (colon is inside the bold)
            match = re.match(r"\*\*(.+?):\*\*\s+(.+)", line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                # Strip single surrounding backticks
                value = re.sub(r"^`(.+?)`$", r"\1", value)
                
                # Normalize key to snake_case
                normalized_key = key.lower()
                normalized_key = re.sub(r"[^a-z0-9]+", "_", normalized_key)
                normalized_key = normalized_key.strip("_")
                
                metadata[normalized_key] = value

        return metadata

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
        header_idx = next(
            (i for i, ln in enumerate(lines) if ln.startswith("|") and ln.endswith("|")), None
        )
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
            if all(v.strip() in {"", "..."} for v in row.values()):
                continue
            rows.append(row)

        return rows

    @staticmethod
    def _find_all_table_blocks(text: str) -> List[str]:
        """Return all markdown table blocks in text."""
        table_re = re.compile(
            r"(\|[^\n]+\|\n\|[-: \|]+\|\n(?:\|[^\n]+\|\n)+)", re.MULTILINE
        )
        return [m.group(1) for m in table_re.finditer(text)]

    @staticmethod
    def _extract_mermaid_blocks(text: str) -> List[str]:
        """Extract all mermaid diagram blocks from text."""
        return [m.group(1).strip() for m in re.finditer(r"```mermaid\s*\n(.*?)```", text, re.DOTALL)]

    @staticmethod
    def _guess_mermaid_kind(mermaid_code: str) -> str:
        """Determine the type of mermaid diagram."""
        first = mermaid_code.strip().splitlines()[0].strip() if mermaid_code.strip() else ""
        if first.startswith("sequenceDiagram"):
            return "sequenceDiagram"
        if first.startswith("flowchart"):
            return "flowchart"
        return "mermaid"

    def _current_tab_entity_id(self) -> Optional[str]:
        """Return the graph entity id for the tab/module this display conditions doc belongs to.

        Maps based on module and tab folder:
        - simple/yuusyou-kihon -> tab:basic_information
        - housing/basic-info-housing-contract -> tab:basic_information_housing
        - contract-list -> module:contract_list (no basic tab)
        """
        if self.module_name == "simple" and self.tab_name == "yuusyou-kihon":
            return "tab:basic_information"
        if self.module_name == "housing" and self.tab_name == "basic-info-housing-contract":
            return "tab:basic_information_housing"
        if self.module_name == "contract-list":
            return "module:contract-list"
        return None

    def process(self) -> Dict[str, Any]:
        """Process the display conditions file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Display conditions file not found: {self.file_path}")

        markdown = self.file_path.read_text(encoding="utf-8")
        doc_title, sections = self._parse_sections(markdown)
        screen_metadata = self._extract_screen_metadata(markdown)

        source_file = str(self.file_path.relative_to(self.base_path)).replace("\\", "/")

        # Create root entity for display conditions
        if self.module_name == "contract-list":
            root_id = f"display_conditions:{self.module_name}"
        else:
            root_id = f"display_conditions:{self.module_name}:{self.tab_name}"
        root_name = doc_title or "Display Conditions"

        # Root entity should NOT have content, only metadata properties
        entities: List[Dict[str, Any]] = [
            {
                "id": root_id,
                "type": "display_conditions",
                "name": root_name,
                "module": self.module_name,
                "tab_name": self.tab_name,
                "source_file": source_file,
                **screen_metadata,  # Include screen metadata as individual properties
            }
        ]

        relationships: List[Dict[str, Any]] = []

        # Link to current tab if available
        current_tab_id = self._current_tab_entity_id()
        if current_tab_id:
            relationships.append(
                {
                    "source": root_id,
                    "target": current_tab_id,
                    "relationship_type": "DESCRIBES",
                    "description": f"Display conditions describe {current_tab_id}",
                }
            )

        # 1) Create heading-based section entities for traceability
        stack: List[Tuple[int, str]] = []  # (heading_level, entity_id)
        slug_counts: Dict[str, int] = {}
        section_id_by_key: Dict[Tuple[int, str], str] = {}

        for section in sections:
            _, clean_title = self._strip_heading_number(section.title_raw)
            base_slug = self._slugify(clean_title)
            slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1
            slug = base_slug if slug_counts[base_slug] == 1 else f"{base_slug}_{slug_counts[base_slug]}"

            if self.module_name == "contract-list":
                section_id = f"display_conditions_section:{self.module_name}:{slug}"
            else:
                section_id = f"display_conditions_section:{self.module_name}:{self.tab_name}:{slug}"
            entities.append(
                {
                    "id": section_id,
                    "type": "display_conditions_section",
                    "name": clean_title,
                    "module": self.module_name,
                    "tab_name": self.tab_name,
                    "source_file": source_file,
                    "heading_level": section.level,
                    "heading_raw": section.title_raw,
                    "content": section.content,
                }
            )

            # Determine parent based on heading nesting
            while stack and stack[-1][0] >= section.level:
                stack.pop()
            parent_id = stack[-1][1] if stack else root_id
            relationships.append(
                {"source": parent_id, "target": section_id, "relationship_type": "HAS_SECTION"}
            )

            stack.append((section.level, section_id))
            section_id_by_key[(section.level, section.title_raw)] = section_id

        # 2) Extract mermaid diagrams from sections
        for section in sections:
            mermaid_blocks = self._extract_mermaid_blocks(section.content)
            if not mermaid_blocks:
                continue

            _, clean_title = self._strip_heading_number(section.title_raw)
            for idx, code in enumerate(mermaid_blocks, start=1):
                kind = self._guess_mermaid_kind(code)
                slug = self._slugify(clean_title)
                if self.module_name == "contract-list":
                    diagram_id = f"display_flow:{self.module_name}:{slug}:{idx}"
                else:
                    diagram_id = f"display_flow:{self.module_name}:{self.tab_name}:{slug}:{idx}"
                entities.append(
                    {
                        "id": diagram_id,
                        "type": "display_flow_diagram",
                        "name": clean_title,
                        "module": self.module_name,
                        "tab_name": self.tab_name,
                        "source_file": source_file,
                        "mermaid_kind": kind,
                        "mermaid": code,
                    }
                )
                relationships.append(
                    {"source": root_id, "target": diagram_id, "relationship_type": "HAS_FLOW"}
                )

                # Link to section
                section_entity_id = section_id_by_key.get((section.level, section.title_raw))
                if section_entity_id:
                    relationships.append(
                        {
                            "source": section_entity_id,
                            "target": diagram_id,
                            "relationship_type": "HAS_DIAGRAM",
                        }
                    )

        return {
            "module": self.module_name,
            "tab_name": self.tab_name,
            "source_file": source_file,
            "entities": entities,
            "relationships": relationships,
        }

    def save_to_json(self, output_path: str | Path) -> None:
        """Save processed results to JSON file."""
        results = self.process()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


def main() -> None:
    """Generate display conditions JSON for all modules."""
    base_path = "/data_hdd_16t/vuongchu/nxGREG/ctc-data-en"
    
    # Process simple module
    simple_processor = DisplayConditionsProcessor(
        base_path, 
        module_name="simple", 
        tab_name="yuusyou-kihon"
    )
    simple_processor.save_to_json(
        "/data_hdd_16t/vuongchu/nxGREG/json/simple/simple-display-conditions.json"
    )
    
    # Process housing module
    housing_processor = DisplayConditionsProcessor(
        base_path, 
        module_name="housing", 
        tab_name="basic-info-housing-contract"
    )
    housing_processor.save_to_json(
        "/data_hdd_16t/vuongchu/nxGREG/json/housing/housing-display-conditions.json"
    )
    
    # Process contract-list module
    contract_list_processor = DisplayConditionsProcessor(
        base_path, 
        module_name="contract-list"
    )
    contract_list_processor.save_to_json(
        "/data_hdd_16t/vuongchu/nxGREG/json/contract-list/contract-list-display-conditions.json"
    )
    
    print("Display conditions JSON files generated successfully!")


if __name__ == "__main__":
    main()
