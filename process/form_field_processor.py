"""
Form Field Processor

This module processes form field markdown files and extracts FormGroup entities
based on field prefixes. It creates relationships between forms, form groups, 
and form fields.

The form groups are logical groupings of related form fields, typically identified
by field name prefixes (e.g., CH01_, J0001_, J0002_, C0001_, etc.).

Author: System
Date: December 10, 2025
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import pandas as pd
import io


class FormFieldProcessor:
    """
    Processes form field documentation to extract FormGroup entities and relationships.
    """
    
    def __init__(self, base_path: str, module_name: str = "simple", screen: str = "yuusyou-kihon"):
        """
        Initialize the processor.
        
        Args:
            base_path: Base path to the ctc-data-en directory
            module_name: Module name (default: "simple")
            screen: Screen name (default: "yuusyou-kihon")
        """
        self.base_path = Path(base_path)
        self.module_name = module_name
        self.screen = screen
        if self.module_name == "contract-list":
            self.components_path = self.base_path / module_name / "components"
        else:
            self.components_path = self.base_path / module_name / screen / "components"
        
        
        # Storage for extracted data
        self.form_groups = []
        self.form_fields = []
        self.form_to_group_relationships = []
        self.field_to_group_relationships = []
        
        # Tracking sets
        self.seen_groups = set()
        self.seen_fields = set()
        self.seen_forms = set()
    
    def extract_form_groups_from_markdown(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract form groups and fields from form-fields markdown file.
        
        Args:
            file_path: Path to the form-fields-en.md file
            
        Returns:
            Dictionary containing extracted form groups and relationships
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract form sections (## 1. formName, ## 2. formName, etc.)
        form_sections = re.findall(
            r'##\s+\d+\.\s+`([^`]+)`(.*?)(?=\n##\s+\d+\.|$)',
            content,
            re.DOTALL
        )
        
        for form_id, form_content in form_sections:
            self._process_form_section(form_id, form_content)
        
        return {
            'form_groups': self.form_groups,
            'form_fields': self.form_fields,
            'form_to_group_relationships': self.form_to_group_relationships,
            'field_to_group_relationships': self.field_to_group_relationships
        }
    
    def _process_form_section(self, form_id: str, form_content: str) -> None:
        """
        Process a single form section to extract groups and fields.
        
        Args:
            form_id: Form identifier (e.g., yuusyou_keiyakuNewtmp_kihonForm)
            form_content: Content of the form section
        """
        # Extract ALL ### subsections (level 3 headers)
        # Pattern matches: ### X.Y. Section Name or ### X.Y. Section Name (PREFIX_)
        all_sections_pattern = r'###\s+[\d\.]+\s+([^(\n]+)(?:\(([^)]+)\))?(.*?)(?=\n###|\Z)'
        section_matches = re.findall(all_sections_pattern, form_content, re.DOTALL)
        
        for section_name, optional_prefix, section_content in section_matches:
            section_name = section_name.strip()
            optional_prefix = optional_prefix.strip() if optional_prefix else None
            
            # Determine the group prefix
            if optional_prefix:
                # Use explicit prefix from parentheses
                group_prefix = optional_prefix
            else:
                # Generate prefix from section name (e.g., "Common Properties" -> "COMMON", "Search Properties" -> "SEARCH")
                group_prefix = section_name.upper().replace(' ', '_').replace('PROPERTIES', '').strip('_')
                if not group_prefix:
                    group_prefix = "COMMON"
            
            # Create unique group identifier
            group_id = f"form_group:{form_id}:{group_prefix}"
            
            # Skip if already processed
            if group_id in self.seen_groups:
                continue
            
            # Extract fields from markdown table (no prefix filtering for sections without explicit prefix)
            filter_by_prefix = optional_prefix if optional_prefix else None
            fields = self._extract_fields_from_table(section_content, filter_by_prefix)
            
            if not fields:
                continue
            
            # Create FormGroup entity
            form_group = {
                'id': group_id,
                'type': 'form_group',
                'name': section_name,
                'parent_module': f"module:{self.module_name}",
                'form_id': form_id,
                'prefix': group_prefix,
                'field_count': len(fields),
                'description': f"{section_name} - Fields with prefix {group_prefix}" if optional_prefix else f"{section_name}",
                'source_file': f"ctc-data-en/{self.module_name}/{self.screen}/components/form-fields-en.md"
            }
            
            self.form_groups.append(form_group)
            self.seen_groups.add(group_id)
            
            # Create relationship: Form -> FormGroup
            self.form_to_group_relationships.append({
                'from': f"form:{form_id}",
                'to': group_id,
                'relationship': 'HAS_GROUP'
            })
            
            # Create individual field entities and relationships
            for field in fields:
                field_id = f"form_field:{field['field_name']}"
                
                # Skip if field already processed
                if field_id in self.seen_fields:
                    continue
                
                # Create FormField entity
                form_field = {
                    'id': field_id,
                    'type': 'form_field',
                    'name': field['field_name'],
                    'parent_module': f"module:{self.module_name}",
                    'form_id': form_id,
                    'field_name': field['field_name'],
                    'data_type': field.get('data_type', ''),
                    'description': field.get('description', ''),
                    'group_prefix': group_prefix,
                    'group_name': section_name,
                    'source_file': f"ctc-data-en/{self.module_name}/{self.screen}/components/form-fields-en.md"
                }
                
                self.form_fields.append(form_field)
                self.seen_fields.add(field_id)
                
                # Create relationship: FormGroup -> FormField
                self.field_to_group_relationships.append({
                    'from': group_id,
                    'to': field_id,
                    'relationship': 'CONTAINS_FIELD'
                })
    
    def _extract_fields_from_table(self, content: str, prefix: str = None) -> List[Dict[str, str]]:
        """
        Extract field information from markdown table.
        
        Args:
            content: Content containing the markdown table
            prefix: Field prefix to filter by (None = extract all fields)
            
        Returns:
            List of field dictionaries
        """
        fields = []
        
        # Find markdown table
        table_pattern = r'\|[^\n]+\|[^\n]+\n\|[-\s|]+\n((?:\|[^\n]+\n)+)'
        table_match = re.search(table_pattern, content)
        
        if not table_match:
            return fields
        
        table_content = table_match.group(0)
        
        try:
            # Parse markdown table using pandas
            clean_table = "\n".join(
                line for line in table_content.splitlines()
                if not set(line.strip()) == {"|", "-", " "}
            )
            
            df = pd.read_csv(io.StringIO(clean_table), sep="|", engine="python")
            df.columns = df.columns.str.strip()
            df = df.dropna(axis=1, how='all')
            
            # Strip whitespace from all string columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
            
            # Extract fields
            for _, row in df.iterrows():
                # Try both 'Field Name' and 'Item Name' column headers
                field_name = row.get('Field Name', row.get('Item Name', ''))
                
                # Skip empty, placeholder, or separator rows
                if not field_name or field_name == '...' or field_name.strip('-') == '':
                    continue
                
                # If prefix is specified, filter by prefix; otherwise extract all
                if prefix is not None and not field_name.startswith(prefix):
                    continue
                
                fields.append({
                    'field_name': field_name,
                    'data_type': row.get('Data Type', ''),
                    'description': row.get('Description', '')
                })
        
        except Exception as e:
            print(f"Error parsing table for prefix {prefix}: {e}")
        
        return fields
    
    def process_all_forms(self) -> Dict[str, Any]:
        """
        Process all form field files in the components directory.
        
        Returns:
            Dictionary containing all extracted data
        """
        form_files = list(self.components_path.glob("*form-fields*.md"))
        
        if not form_files:
            print(f"No form field files found in {self.components_path}")
            return self._get_results()
        
        for form_file in form_files:
            print(f"Processing: {form_file.name}")
            self.extract_form_groups_from_markdown(form_file)
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        """
        Get all processed results in Neo4j compatible format.
        
        Returns:
            Dictionary containing entities and relationships lists
        """
        # Combine all entities
        entities = self.form_groups + self.form_fields
        
        # Convert relationships to Neo4j format
        relationships = []
        
        # Convert form-to-group relationships
        for rel in self.form_to_group_relationships:
            relationships.append({
                'source': rel['from'],
                'target': rel['to'],
                'relationship_type': rel['relationship']
            })
        
        # Convert field-to-group relationships
        for rel in self.field_to_group_relationships:
            relationships.append({
                'source': rel['from'],
                'target': rel['to'],
                'relationship_type': rel['relationship']
            })
        
        return {
            'entities': entities,
            'relationships': relationships
        }
    
    def save_to_json(self, output_path: Path) -> None:
        """
        Save extracted data to JSON file.
        
        Args:
            output_path: Path to save the JSON file
        """
        results = self._get_results()
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved results to: {output_path}")
        print(f"Total Entities: {len(results['entities'])}")
        print(f"  - Form Groups: {len(self.form_groups)}")
        print(f"  - Form Fields: {len(self.form_fields)}")
        print(f"Total Relationships: {len(results['relationships'])}")


def main():
    """Main execution function."""
    import sys
    
    # Get base path from command line or use default
    base_path = sys.argv[1] if len(sys.argv) > 1 else "ctc-data-en"
    module_name = sys.argv[2] if len(sys.argv) > 2 else "contract-list"
    screen = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Initialize processor
    processor = FormFieldProcessor(base_path, module_name, screen)
    
    # Process all forms
    results = processor.process_all_forms()
    
    # Save to JSON
    output_dir = Path("json") / module_name
    output_file = output_dir / f"{module_name}-form-groups.json"
    processor.save_to_json(output_file)
    
    # Print summary
    print("\n" + "="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"Module: {module_name}")
    print(f"Screen: {screen}")
    print(f"Total Entities: {len(results['entities'])}")
    print(f"  - Form Groups: {len([e for e in results['entities'] if e['type'] == 'form_group'])}")
    print(f"  - Form Fields: {len([e for e in results['entities'] if e['type'] == 'form_field'])}")
    print(f"Total Relationships: {len(results['relationships'])}")
    print("="*80)


if __name__ == "__main__":
    main()
