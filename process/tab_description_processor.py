"""
Tab Description Processor

This module processes out-of-scope tab description markdown files from both simple 
and housing modules. These files describe how the main Basic Information tab affects 
other tabs (Accounting, Order, Cancellation, etc.).

Each description file contains:
1. Overview section - general information about the tab
2. Processing Flow section - mermaid diagram showing tab navigation flow
3. Impact section - table showing how basic information changes affect the tab

Author: System
Date: December 10, 2025
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import io


class TabDescriptionProcessor:
    """
    Processes tab description files to extract entities from overview, 
    processing flow, and impact sections.
    """
    
    def __init__(self, base_path: str, module_name: str = "simple"):
        """
        Initialize the processor.
        
        Args:
            base_path: Base path to the ctc-data-en directory
            module_name: Module name ("simple" or "housing")
        """
        self.base_path = Path(base_path)
        self.module_name = module_name
        self.module_path = self.base_path / module_name
        self.entities = []
        self.relationships = []
    
    def find_description_files(self) -> List[Path]:
        """
        Find all description_*_init_screen*.md files in the module.
        
        Returns:
            List of paths to description files (deduplicated)
        """
        description_files = set()
        
        # Search for description files in all subdirectories
        # Use set to avoid duplicates from overlapping patterns
        for pattern in ["description_*_init_screen*.md"]:
            description_files.update(self.module_path.rglob(pattern))
        
        return sorted(list(description_files))
    
    def extract_tab_name_from_path(self, file_path: Path) -> str:
        """
        Extract tab name from file path.
        
        Args:
            file_path: Path to description file
            
        Returns:
            Tab name (e.g., "accounting-info-simple-contract")
        """
        # Get the parent directory name
        return file_path.parent.name
    
    def extract_overview_section(self, content: str, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract the Overview section as a single entity.
        
        Args:
            content: Full markdown content
            file_path: Path to the file
            
        Returns:
            Overview entity dict or None
        """
        # Find Overview section
        overview_pattern = r'##\s+Overview\s*\n(.*?)(?=\n##\s+|\Z)'
        overview_match = re.search(overview_pattern, content, re.DOTALL)
        
        if not overview_match:
            return None
        
        overview_content = overview_match.group(1).strip()
        
        # Extract table data from overview
        overview_data = self._parse_overview_table(overview_content)
        
        tab_name = self.extract_tab_name_from_path(file_path)
        
        entity = {
            "id": f"tab-desc:{self.module_name}:{tab_name}:overview",
            "type": "TabOverview",
            "name": overview_data.get("Screen Name", "Unknown Tab"),
            "module": self.module_name,
            "tab_name": tab_name,
            "main_function": overview_data.get("Main Function", ""),
            "contract_type": overview_data.get("Contract Type", ""),
            "document_purpose": overview_data.get("Document Purpose", ""),
            "analysis_scope": overview_data.get("Analysis Scope", ""),
            "source_file": str(file_path.relative_to(self.base_path)),
            "section_title": "Overview"
        }
        
        return entity
    
    def _parse_overview_table(self, overview_content: str) -> Dict[str, str]:
        """
        Parse the overview table to extract key-value pairs.
        
        Args:
            overview_content: Content of overview section
            
        Returns:
            Dictionary of overview information
        """
        overview_data = {}
        
        # Match markdown table rows
        row_pattern = r'\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|'
        matches = re.findall(row_pattern, overview_content)
        
        for key, value in matches:
            overview_data[key.strip()] = value.strip()
        
        return overview_data
    
    def extract_processing_flow_section(self, content: str, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract the Processing Flow section with mermaid diagram.
        
        Args:
            content: Full markdown content
            file_path: Path to the file
            
        Returns:
            Processing flow entity dict or None
        """
        # Find the first numbered section (usually "1. Tab Click Processing...")
        flow_pattern = r'##\s+(\d+)\.\s+(Tab Click Processing.*?|.*?Processing.*?)\s*\n(.*?)(?=\n##\s+|\Z)'
        flow_match = re.search(flow_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not flow_match:
            return None
        
        section_number = flow_match.group(1)
        section_title = flow_match.group(2).strip()
        section_content = flow_match.group(3).strip()
        
        # Extract mermaid diagram
        mermaid_pattern = r'```mermaid\s*\n(.*?)```'
        mermaid_match = re.search(mermaid_pattern, section_content, re.DOTALL)
        
        mermaid_content = ""
        if mermaid_match:
            mermaid_content = mermaid_match.group(1).strip()
        
        tab_name = self.extract_tab_name_from_path(file_path)
        
        entity = {
            "id": f"tab-desc:{self.module_name}:{tab_name}:flow",
            "type": "TabProcessingFlow",
            "name": section_title,
            "module": self.module_name,
            "tab_name": tab_name,
            "source_file": str(file_path.relative_to(self.base_path)),
            "section_title": section_title,
            "mermaid_diagram": mermaid_content
        }
        
        return entity
    
    def extract_data_display_section(self, content: str, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract the "Data displayed in the [Tab]" section with JSP files list.
        This section appears in housing module files.
        
        Args:
            content: Full markdown content
            file_path: Path to the file
            
        Returns:
            Data display entity dict or None
        """
        # Find "Data displayed in" section
        data_display_pattern = r'###\s+(Data displayed.*?)\s*\n(.*?)(?=\n###\s+|\n\|\s+Change|\Z)'
        data_display_match = re.search(data_display_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not data_display_match:
            return None
        
        section_title = data_display_match.group(1).strip()
        section_content = data_display_match.group(2).strip()
        
        # Extract JSP files from bullet list
        jsp_files = self._parse_jsp_files(section_content)
        
        if not jsp_files:
            return None
        
        tab_name = self.extract_tab_name_from_path(file_path)
        
        # Create a list of "file: description" strings for Neo4j compatibility
        jsp_files_list = [jsp["file"] for jsp in jsp_files]
        jsp_descriptions_list = [f"{jsp['file']}: {jsp['description']}" for jsp in jsp_files]
        
        entity = {
            "id": f"tab-desc:{self.module_name}:{tab_name}:data-display",
            "type": "TabDataDisplay",
            "name": section_title,
            "module": self.module_name,
            "tab_name": tab_name,
            "source_file": str(file_path.relative_to(self.base_path)),
            "section_title": section_title,
            "jsp_files": jsp_files_list,
            "jsp_descriptions": jsp_descriptions_list
        }
        
        return entity
    
    def _parse_jsp_files(self, content: str) -> List[Dict[str, str]]:
        """
        Parse JSP file list from content.
        
        Expected format:
        - **A0020.jsp**: Collection Information
        - **A0002.jsp**: Collection Conditions
        
        Args:
            content: Section content
            
        Returns:
            List of dicts with 'file' and 'description' keys
        """
        jsp_files = []
        
        # Match JSP file entries
        jsp_pattern = r'-\s+\*\*([A-Z][0-9]{4}\.jsp)\*\*:\s+(.+?)(?=\n|$)'
        matches = re.findall(jsp_pattern, content, re.MULTILINE)
        
        for file_name, description in matches:
            jsp_files.append({
                "file": file_name,
                "description": description.strip()
            })
        
        return jsp_files
    
    def extract_impact_section(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract the Impact section table and create separate entities for each impact type.
        
        Args:
            content: Full markdown content
            file_path: Path to the file
            
        Returns:
            List of impact entity dicts
        """
        # Find Impact section (usually "2. Impact from Tab Basic Information")
        impact_pattern = r'##\s+(\d+)\.\s+(Impact.*?)\s*\n(.*?)(?=\n##\s+|\Z)'
        impact_match = re.search(impact_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not impact_match:
            return []
        
        section_number = impact_match.group(1)
        section_title = impact_match.group(2).strip()
        section_content = impact_match.group(3).strip()
        
        # Extract table from section
        impacts = self._parse_impact_table(section_content)
        
        tab_name = self.extract_tab_name_from_path(file_path)
        
        entities = []
        for impact in impacts:
            entity = {
                "id": f"tab-desc:{self.module_name}:{tab_name}:impact:{self._slugify(impact['change_type'])}",
                "type": "TabImpact",
                "name": impact["change_type"],
                "module": self.module_name,
                "tab_name": tab_name,
                "source_file": str(file_path.relative_to(self.base_path)),
                "section_title": section_title,
                "change_type": impact["change_type"],
                "database_impact": impact.get("database_impact", ""),
                "action_impact": impact.get("action_impact", ""),
                "ui_impact": impact.get("ui_impact", "")
            }
            entities.append(entity)
        
        return entities
    
    def _parse_impact_table(self, section_content: str) -> List[Dict[str, str]]:
        """
        Parse the impact table using pandas.
        
        Args:
            section_content: Content of impact section
            
        Returns:
            List of impact dictionaries
        """
        impacts = []
        
        # Find the table in the content
        lines = section_content.split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            if '|' in line:
                in_table = True
                # Skip separator lines
                if not re.match(r'^\s*\|[\s\-:]+\|', line):
                    table_lines.append(line)
            elif in_table and line.strip() == '':
                break
        
        if not table_lines:
            return impacts
        
        # Join table lines
        table_content = '\n'.join(table_lines)
        
        try:
            # Read as pipe-separated
            df = pd.read_csv(io.StringIO(table_content), sep="|", engine="python")
            
            # Clean column names (strip whitespace)
            df.columns = df.columns.str.strip()
            
            # Drop completely empty columns
            df = df.dropna(axis=1, how='all')
            
            # Strip whitespace from all string columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
            
            # Remove rows where all values are NaN
            df = df.dropna(how='all')
            
            # Convert DataFrame to list of dicts
            for _, row in df.iterrows():
                impact = {}
                
                # Map columns to standard keys
                for col in df.columns:
                    col_lower = col.lower()
                    if 'change' in col_lower and 'type' in col_lower:
                        impact['change_type'] = str(row[col])
                    elif 'database' in col_lower:
                        impact['database_impact'] = str(row[col])
                    elif 'action' in col_lower:
                        impact['action_impact'] = str(row[col])
                    elif 'ui' in col_lower:
                        impact['ui_impact'] = str(row[col])
                
                if impact.get('change_type') and impact['change_type'] != 'nan':
                    impacts.append(impact)
        
        except Exception as e:
            print(f"Error parsing impact table: {e}")
            # Fallback to manual parsing
            impacts = self._manual_parse_impact_table(table_lines)
        
        return impacts
    
    def _manual_parse_impact_table(self, table_lines: List[str]) -> List[Dict[str, str]]:
        """
        Manual fallback parsing for impact tables.
        
        Args:
            table_lines: Lines of the table
            
        Returns:
            List of impact dictionaries
        """
        impacts = []
        
        if len(table_lines) < 2:
            return impacts
        
        # Parse header
        header = [col.strip() for col in table_lines[0].split('|') if col.strip()]
        
        # Parse data rows (skip header and separator)
        for line in table_lines[1:]:
            if '---' in line or not line.strip():
                continue
            
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            
            if len(cells) >= len(header):
                impact = {}
                for i, col in enumerate(header):
                    col_lower = col.lower()
                    if 'change' in col_lower and 'type' in col_lower:
                        impact['change_type'] = cells[i]
                    elif 'database' in col_lower:
                        impact['database_impact'] = cells[i]
                    elif 'action' in col_lower:
                        impact['action_impact'] = cells[i]
                    elif 'ui' in col_lower:
                        impact['ui_impact'] = cells[i]
                
                if impact.get('change_type'):
                    impacts.append(impact)
        
        return impacts
    
    def _slugify(self, text: str) -> str:
        """
        Convert text to slug format for IDs.
        
        Args:
            text: Text to slugify
            
        Returns:
            Slugified text
        """
        # Remove ** markdown bold
        text = re.sub(r'\*\*', '', text)
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _map_tab_folder_to_tab_id(self, tab_folder_name: str) -> str:
        """
        Map tab folder name to actual tab entity ID.
        
        Args:
            tab_folder_name: Folder name like "accounting-info-simple-contract"
            
        Returns:
            Tab entity ID like "tab:accounting_information"
        """
        # Mapping of folder names to tab IDs
        tab_mappings = {
            "accounting-info-simple-contract": "tab:accounting_information",
            "order-info-simple-contract": "tab:order_information",
            "cancel-info-simple-contract": "tab:cancellation_information",
            "accounting-registration": "tab:accounting_registration",
            "basic-info-housing-contract": "tab:basic_information_housing",
            "cancellation-info": "tab:cancellation_information_housing",
            "change-info": "tab:change_information",
            "collection-conditions": "tab:collection_conditions",
            "contruction-planning": "tab:construction_planning",
            "loan-info": "tab:loan_information",
            "obstacle-factors": "tab:obstacle_factors",
            "order-info": "tab:order_information_housing",
            "supplementary-contract-info": "tab:supplementary_contract_info",
            "various-expenses-&-special-terms": "tab:various_expenses_special_terms"
        }
        
        return tab_mappings.get(tab_folder_name, f"tab:{tab_folder_name.replace('-', '_')}")
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single description file and extract all entities.
        
        Args:
            file_path: Path to description file
            
        Returns:
            Dictionary containing entities and relationships
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        entities = []
        relationships = []
        
        tab_name = self.extract_tab_name_from_path(file_path)
        tab_entity_id = self._map_tab_folder_to_tab_id(tab_name)
        
        # Extract overview
        overview_entity = self.extract_overview_section(content, file_path)
        if overview_entity:
            entities.append(overview_entity)
            
            # Create relationship from overview to actual tab entity
            relationships.append({
                "source": overview_entity["id"],
                "target": tab_entity_id,
                "relationship_type": "DESCRIBES",
                "description": f"Overview describes {tab_entity_id}"
            })
        
        # Extract processing flow
        flow_entity = self.extract_processing_flow_section(content, file_path)
        if flow_entity:
            entities.append(flow_entity)
            
            # Create relationship from flow to actual tab entity
            relationships.append({
                "source": flow_entity["id"],
                "target": tab_entity_id,
                "relationship_type": "DESCRIBES_FLOW",
                "description": f"Processing flow describes navigation to {tab_entity_id}"
            })
        
        # Extract data display section (housing module specific)
        data_display_entity = self.extract_data_display_section(content, file_path)
        if data_display_entity:
            entities.append(data_display_entity)
            
            # Create relationship from data display to actual tab entity
            relationships.append({
                "source": data_display_entity["id"],
                "target": tab_entity_id,
                "relationship_type": "DISPLAYS_DATA",
                "description": f"Data display section describes JSP files shown in {tab_entity_id}"
            })
            
            # Create relationships from data display to JSP files (if they exist as entities)
            for jsp_file in data_display_entity["jsp_files"]:
                jsp_entity_id = f"jsp:{jsp_file.replace('.jsp', '').lower()}"
                relationships.append({
                    "source": data_display_entity["id"],
                    "target": jsp_entity_id,
                    "relationship_type": "REFERENCES_JSP",
                    "description": f"References JSP file {jsp_file}"
                })
        
        # Extract impacts
        impact_entities = self.extract_impact_section(content, file_path)
        for impact_entity in impact_entities:
            entities.append(impact_entity)
            
            # Create relationship from impact to actual tab entity
            relationships.append({
                "source": impact_entity["id"],
                "target": tab_entity_id,
                "relationship_type": "IMPACTS",
                "description": f"{impact_entity['change_type']} impacts {tab_entity_id}"
            })
        
        return {
            "file_path": str(file_path.relative_to(self.base_path)),
            "tab_name": tab_name,
            "tab_entity_id": tab_entity_id,
            "entities": entities,
            "relationships": relationships
        }
    
    def process_all_files(self) -> Dict[str, Any]:
        """
        Process all description files in the module.
        
        Returns:
            Dictionary containing all entities and relationships
        """
        description_files = self.find_description_files()
        
        all_entities = []
        all_relationships = []
        
        for file_path in description_files:
            print(f"Processing: {file_path.relative_to(self.base_path)}")
            result = self.process_file(file_path)
            all_entities.extend(result["entities"])
            all_relationships.extend(result["relationships"])
        
        # Add relationships between basic information tab and other tabs
        # For simple module, use tab:basic_information
        # For housing module, use tab:basic_information_housing or appropriate ID
        basic_info_id = "tab:basic_information" if self.module_name == "simple" else "tab:basic_information_housing"
        
        # Create relationships from basic info to each tab (not to overview entities)
        processed_tabs = set()
        for file_path in description_files:
            tab_name = self.extract_tab_name_from_path(file_path)
            tab_entity_id = self._map_tab_folder_to_tab_id(tab_name)
            
            if tab_entity_id not in processed_tabs:
                all_relationships.append({
                    "source": basic_info_id,
                    "target": tab_entity_id,
                    "relationship_type": "AFFECTS",
                    "description": f"Basic Information tab affects {tab_entity_id}"
                })
                processed_tabs.add(tab_entity_id)
        
        return {
            "module": self.module_name,
            "total_files": len(description_files),
            "total_entities": len(all_entities),
            "total_relationships": len(all_relationships),
            "entities": all_entities,
            "relationships": all_relationships
        }
    
    def save_to_json(self, output_path: str):
        """
        Process all files and save results to JSON.
        
        Args:
            output_path: Path to output JSON file
        """
        results = self.process_all_files()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved results to: {output_file}")
        print(f"  - Total files processed: {results['total_files']}")
        print(f"  - Total entities: {results['total_entities']}")
        print(f"  - Total relationships: {results['total_relationships']}")


def main():
    """Main execution function."""
    import sys
    
    # Get base path from command line or use default
    base_path = sys.argv[1] if len(sys.argv) > 1 else "ctc-data-en"
    module_name = sys.argv[2] if len(sys.argv) > 2 else "housing"
    
    processor = TabDescriptionProcessor(base_path, module_name)
    
    # Save to JSON
    output_path = f"json/{module_name}/{module_name}-tab-descriptions.json"
    processor.save_to_json(output_path)


if __name__ == "__main__":
    main()
