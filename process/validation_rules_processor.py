"""
Processor for validation-rules-en.md files.

Parses validation rules documentation into graph entities and relationships.
"""

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


class ValidationRulesProcessor:
    """Parse validation rules markdown into graph entities + relationships."""

    def __init__(
        self,
        base_path: str | Path,
        module_name: str = "simple",
        basic_tab_name: Optional[str] = None,
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

        if module_name == "contract-list":
            # contract-list has no tab folder, goes directly to components
            self.file_path = (
                self.base_path
                / self.module_name
                / "components"
                / "validation-rules-en.md"
            )
        else:
            # simple and housing have tab folders
            self.file_path = (
                self.base_path
                / self.module_name
                / self.basic_tab_name
                / "components"
                / "validation-rules-en.md"
            )

    @staticmethod
    def _strip_heading_number(title: str) -> Tuple[Optional[str], str]:
        """Return (section_number, clean_title)."""
        raw = title.strip()

        # Pattern A: requires trailing dot after the number block (e.g., "1. Title", "2.1. Title")
        m = re.match(r"^(\d+(?:\.\d+)*)\.\s+(.+?)\s*$", raw)
        if m:
            return m.group(1), m.group(2).strip()

        # Pattern B: number block followed by whitespace (e.g., "2.1 Title", "2.1.1 Title")
        m = re.match(r"^(\d+(?:\.\d+)+)\s+(.+?)\s*$", raw)
        if m:
            return m.group(1), m.group(2).strip()

        return None, raw

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"`", "", text)
        text = re.sub(r"[^a-z0-9_\-\s]", "", text)
        text = re.sub(r"[\s\-]+", "_", text)
        return text.strip("_") or "section"

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
    def _extract_original_file_location(markdown: str) -> Optional[str]:
        """Extract the original file location from the markdown content.
        
        Expected format:
        ## Original File Location
        ```
        src/webapp/dsmart/docroot/contract/yuusyou/keiyakuNewtmp/kihon.jsp
        ```
        
        or:
        ## Original File Path
        ```
        src/webapp/dsmart/docroot/contract/ukeoi/keiyakuNewtmp/kihon.jsp
        ```
        """
        # Look for "Original File Location" or "Original File Path" section
        pattern = r"##\s+Original File (?:Location|Path)\s*```\s*([^\n`]+)\s*```"
        match = re.search(pattern, markdown, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def process(self) -> Dict[str, Any]:
        """Process the module/tab validation rules file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Validation rules file not found: {self.file_path}")

        markdown = self.file_path.read_text(encoding="utf-8")
        doc_title, sections = self._parse_sections(markdown)

        source_file = str(self.file_path.relative_to(self.base_path)).replace("\\", "/")

        # Extract original file location if present
        original_file_location = self._extract_original_file_location(markdown)

        # Create base entity ID and properties
        root_id = f"validation_rules:{self.module_name}:{self.basic_tab_name}"
        root_name = doc_title or f"{self.basic_tab_name} validation rules"

        base_props: Dict[str, Any] = {
            "id": root_id,
            "type": "validation_rules",
            "name": root_name,
            "module": self.module_name,
            "tab_name": self.basic_tab_name,
            "source_file": source_file,
        }

        # Add original_file_location as a property if it exists
        if original_file_location:
            base_props["original_file_location"] = original_file_location

        entities: List[Dict[str, Any]] = [base_props]

        relationships: List[Dict[str, Any]] = []

        # Build heading-based entities (all headings level 2+)
        stack: List[Tuple[int, str]] = []  # (heading_level, entity_id)
        slug_counts: Dict[str, int] = {}
        
        for section in sections:
            section_number, clean_title = self._strip_heading_number(section.title_raw)

            # Skip "Original File Location" or "Original File Path" section - it's a property, not an entity
            if clean_title.lower() in ["original file location", "original file path"]:
                continue

            base_slug = self._slugify(clean_title)
            slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1
            slug = base_slug if slug_counts[base_slug] == 1 else f"{base_slug}_{slug_counts[base_slug]}"
            section_id = f"validation_rules_section:{self.module_name}:{self.basic_tab_name}:{slug}"

            entities.append(
                {
                    "id": section_id,
                    "type": "validation_rules_section",
                    "name": clean_title,
                    "module": self.module_name,
                    "tab_name": self.basic_tab_name,
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
                {
                    "source": parent_id,
                    "target": section_id,
                    "relationship_type": "HAS_SECTION",
                }
            )

            stack.append((section.level, section_id))

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
        output_path = f"/data_hdd_16t/vuongchu/nxGREG/json/{module}/{module}-validation-rules.json"
        
        # contract-list has no basic tab, so basic_tab_name will be auto-set in __init__
        processor = ValidationRulesProcessor(base_path, module_name=module)
        processor.save_to_json(output_path)
        print(f"Processed {module} validation rules -> {output_path}")
    
    print("Validation rules JSON files generated successfully!")


if __name__ == "__main__":
    main()
