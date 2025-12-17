

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


class FormValidationProcessor:
    """Parse form validation spec markdown into graph entities + relationships."""

    def __init__(
        self,
        base_path: str | Path,
        module_name: str = "simple",
        basic_tab_name: Optional[str] = None,
    ) -> None:
        self.base_path = Path(base_path)
        self.module_name = module_name

        if basic_tab_name is None:
            self.basic_tab_name = (
                "yuusyou-kihon" if module_name == "simple" else "basic-info-housing-contract"
            )
            self.file_path = (
                self.base_path
                / self.module_name
                / self.basic_tab_name   
                / "screen-specification"
                / "validation_form-en.md"
            )
        elif module_name == "contract-list":
            self.file_path = (
                self.base_path
                / self.module_name
                / "screen-specification"
                / "validation_form-en.md"
            )
        else:
            self.basic_tab_name = basic_tab_name



    @staticmethod
    def _strip_heading_number(title: str) -> Tuple[Optional[str], str]:
        """Return (section_number, clean_title)."""
        # Examples:
        #   "1. Form Settings" -> ("1", "Form Settings")
        #   "2.1 Message Reference Table" -> ("2.1", "Message Reference Table")
        #   "2.1.1 Field Name Messages" -> ("2.1.1", "Field Name Messages")
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
    def _extract_form_settings(section_content: str) -> Dict[str, str]:
        """Extract core properties from the "Form Settings" section.

        Expected format (bullet list):
        - **Form Name**: `...`
        """
        settings: Dict[str, str] = {}
        for key, value in re.findall(
            r"^\s*-\s*\*\*(.+?)\*\*\s*:\s*(.+?)\s*$",
            section_content,
            flags=re.MULTILINE,
        ):
            clean_value = value.strip()
            # Strip single surrounding backticks
            clean_value = re.sub(r"^`(.+?)`$", r"\1", clean_value)
            settings[key.strip()] = clean_value

        def normalize_key(raw_key: str) -> str:
            k = raw_key.strip().lower()
            k = re.sub(r"[\s\-_/]+", " ", k)
            k = re.sub(r"[^a-z0-9\s]", "", k)
            return k.strip()

        # Normalize to snake_case keys used in entities.
        # Accept common variations found in different modules.
        normalized: Dict[str, str] = {}
        key_map = {
            "form name": "form_name",
            "formname": "form_name",
            "action mapping": "action_mapping",
            "action class": "action_class",
            "validation file": "validation_file",
            "struts configuration": "struts_configuration",
            "struts config": "struts_configuration",
            "struts config file": "struts_configuration",
        }

        for raw_key, value in settings.items():
            out_key = key_map.get(normalize_key(raw_key))
            if out_key:
                normalized[out_key] = value

        return normalized

    def process(self) -> Dict[str, Any]:
        """Process the module/tab validation form file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Validation form file not found: {self.file_path}")

        markdown = self.file_path.read_text(encoding="utf-8")
        doc_title, sections = self._parse_sections(markdown)

        source_file = str(self.file_path.relative_to(self.base_path)).replace("\\", "/")

        # Extract base properties from "## 1." section (if present)
        base_props: Dict[str, str] = {}
        for section in sections:
            section_number, _ = self._strip_heading_number(section.title_raw)
            if section.level == 2 and section_number == "1":
                base_props = self._extract_form_settings(section.content)
                break

        form_name = base_props.get("form_name")
        if not form_name:
            raise ValueError(
                f"Could not find 'Form Name' in section '## 1.' for file: {source_file}"
            )

        root_id = f"form_validation:{form_name}"
        form_id = f"form:{form_name}"

        root_name = form_name or doc_title or f"{self.basic_tab_name} validation"

        entities: List[Dict[str, Any]] = [
            {
                "id": root_id,
                "type": "form_validation",
                "name": root_name,
                "module": self.module_name,
                "tab_name": self.basic_tab_name,
                "source_file": source_file,
                "content": markdown.strip(),
                **base_props,
            }
        ]

        relationships: List[Dict[str, Any]] = [
            {
                "source": root_id,
                "target": form_id,
                "relationship_type": "APPLIES_TO_FORM",
            }
        ]

        # Build heading-based entities (all headings level 2+)
        stack: List[Tuple[int, str]] = []  # (heading_level, entity_id)
        slug_counts: Dict[str, int] = {}
        for section in sections:
            section_number, clean_title = self._strip_heading_number(section.title_raw)

            # The base entity already includes the '## 1.' form settings properties.
            # Do not create a duplicate section entity for it.
            if section.level == 2 and section_number == "1":
                continue

            base_slug = self._slugify(clean_title)
            slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1
            slug = base_slug if slug_counts[base_slug] == 1 else f"{base_slug}_{slug_counts[base_slug]}"
            section_id = f"form_validation_section:{form_name}:{slug}"

            entities.append(
                {
                    "id": section_id,
                    "type": "form_validation_section",
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
    import argparse
    
    base_path = "/data_hdd_16t/vuongchu/nxGREG/ctc-data-en"
    modules = ["housing", "simple", "contract-list"]
    
    for module in modules:
        output_path = f"/data_hdd_16t/vuongchu/nxGREG/json/{module}/{module}-form-validation.json"
        basic_tab = "yuusyou-kihon" if module == "simple" else "basic-info-housing-contract"
 
 
        processor = FormValidationProcessor(base_path, module_name=module, basic_tab_name=basic_tab)
        processor.save_to_json(output_path)


if __name__ == "__main__":
    main()
