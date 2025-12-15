"""
Flow Entity Processor

This module processes flow diagram markdown files from function directories
and extracts flow entities with their mermaid diagrams. It processes:
1. sequence-diagram-en.md - Detailed sequence flows
2. function-overview-en.md - High-level process flow (Section 3)

It also creates relationships between flow entities and their parent functions.

Author: System
Date: December 8, 2025
Updated: December 15, 2025
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class FlowEntityProcessor:
    """
    Processes flow diagram files to extract flow entities and establish
    relationships with functions.
    
    Processes two types of files:
    - sequence-diagram-en.md: Detailed implementation flows
    - function-overview-en.md: High-level process flow overview (Section 3)
    """
    
    def __init__(self, base_path: str, module_name: str = "simple"):
        """
        Initialize the processor.
        
        Args:
            base_path: Base path to the ctc-data-en directory
            module_name: Module name (default: "simple")
        """
        self.base_path = Path(base_path)
        self.module_name = module_name
        self.basic_tab_name = "yuusyou-kihon" if module_name == "simple" else "basic-info-housing-contract"
        self.module_path = self.base_path / module_name / self.basic_tab_name / "functions"
        self.entities = []
        self.relationships = []
    
    def extract_sections_from_markdown(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract sections with headings and mermaid diagrams from markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of sections with title and content
        """
        sections = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by headings (## or ###)
        # Pattern to match heading and content until next heading or end
        heading_pattern = r'^(#{2,3})\s+(.+?)$'
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        in_mermaid = False
        mermaid_content = []
        
        for line in lines:
            # Check if this is a heading
            heading_match = re.match(heading_pattern, line)
            
            if heading_match:
                # Save previous section if exists
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'mermaid': '\n'.join(mermaid_content).strip() if mermaid_content else None
                    })
                
                # Start new section
                current_section = heading_match.group(2).strip()
                current_content = []
                mermaid_content = []
                in_mermaid = False
            else:
                # Check for mermaid code block
                if line.strip().startswith('```mermaid'):
                    in_mermaid = True
                    mermaid_content = []
                elif line.strip() == '```' and in_mermaid:
                    in_mermaid = False
                elif in_mermaid:
                    mermaid_content.append(line)
                
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip(),
                'mermaid': '\n'.join(mermaid_content).strip() if mermaid_content else None
            })
        
        return sections
    
    def strip_bullet_number(self, title: str) -> str:
        """
        Strip bullet numbers from the beginning of titles.
        
        Examples:
            "1. Edit Operation" -> "Edit Operation"
            "2.1 Visual Sequence Flow" -> "Visual Sequence Flow"
            "3) Update Process" -> "Update Process"
            
        Args:
            title: Title that may contain bullet numbers
            
        Returns:
            Title with bullet numbers removed
        """
        # Pattern matches: "1.", "1)", "1.1", "1.1.", etc. at the start
        pattern = r'^\s*\d+(\.\d+)*[\.)]\s*'
        return re.sub(pattern, '', title).strip()
    
    def generate_flow_id(self, function_name: str, section_title: str) -> str:
        """
        Generate a unique ID for a flow entity.
        
        Args:
            function_name: Name of the function (with hyphens, e.g., "init-screen")
            section_title: Title of the section
            
        Returns:
            Generated ID in format "flow:function_name:section_slug" with underscores
        """
        # Convert function name from hyphens to underscores to match entity ID format
        function_name_normalized = function_name.replace('-', '_')
        
        # Strip bullet numbers first
        clean_title = self.strip_bullet_number(section_title)
        
        # Convert section title to slug
        section_slug = re.sub(r'[^\w\s-]', '', clean_title.lower())
        section_slug = re.sub(r'[-\s]+', '_', section_slug)
        
        return f"flow:{function_name_normalized}:{section_slug}"
    
    def process_sequence_diagram(self, function_name: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single sequence diagram file and extract flow entities.
        
        Args:
            function_name: Name of the function (from directory name, e.g., "init-screen")
            file_path: Path to the sequence diagram file
            
        Returns:
            List of flow entities extracted from the file
        """
        flow_entities = []
        
        # Convert function name from hyphens to underscores to match entity ID format
        function_name_normalized = function_name.replace('-', '_')
        
        # Extract sections from markdown
        sections = self.extract_sections_from_markdown(file_path)
        
        # Get relative path for source_file
        relative_path = file_path.relative_to(self.base_path.parent)
        
        for section in sections:
            # Only process sections that have mermaid diagrams
            if section['mermaid']:
                # Strip bullet numbers from title
                clean_title = self.strip_bullet_number(section['title'])
                flow_id = self.generate_flow_id(function_name, section['title'])
                
                entity = {
                    "id": flow_id,
                    "type": "process_flow",
                    "name": clean_title,
                    "function_name": function_name_normalized,
                    "parent_function": f"function:{function_name_normalized}",
                    "source_file": str(relative_path).replace('\\', '/'),
                    "section_title": clean_title,
                    "content": section['mermaid'],
                    "description": f"Process flow for {clean_title} in {function_name_normalized} function"
                }
                
                flow_entities.append(entity)
        
        return flow_entities
    
    def process_function_overview(self, function_name: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process function overview file and extract the Process Flow section.
        
        Args:
            function_name: Name of the function (from directory name, e.g., "init-screen")
            file_path: Path to the function-overview-en.md file
            
        Returns:
            List containing the process flow entity (if found)
        """
        flow_entities = []
        
        # Convert function name from hyphens to underscores to match entity ID format
        function_name_normalized = function_name.replace('-', '_')
        
        # Extract sections from markdown
        sections = self.extract_sections_from_markdown(file_path)
        
        # Get relative path for source_file
        relative_path = file_path.relative_to(self.base_path.parent)
        
        # Look for the "Process Flow" section
        for section in sections:
            # Check if this is the Process Flow section (handle variations)
            clean_title = self.strip_bullet_number(section['title'])
            if clean_title.lower() in ['process flow', 'processing flow', 'workflow']:
                # Only process if it has a mermaid diagram
                if section['mermaid']:
                    flow_id = f"flow:{function_name_normalized}:overview_process_flow"
                    
                    entity = {
                        "id": flow_id,
                        "type": "process_flow_overview",
                        "name": f"{function_name_normalized} - Process Flow Overview",
                        "function_name": function_name_normalized,
                        "parent_function": f"function:{function_name_normalized}",
                        "source_file": str(relative_path).replace('\\', '/'),
                        "section_title": clean_title,
                        "content": section['mermaid'],
                        "description": f"High-level process flow overview for {function_name_normalized} function"
                    }
                    
                    flow_entities.append(entity)
                    break  # Only take the first Process Flow section
        
        return flow_entities
    
    def process_all_functions(self) -> None:
        """
        Process all function directories and extract flow entities from both
        sequence-diagram-en.md and function-overview-en.md files.
        """
        if not self.module_path.exists():
            raise FileNotFoundError(f"Module path not found: {self.module_path}")
        
        # Iterate through function directories
        for function_dir in self.module_path.iterdir():
            if function_dir.is_dir():
                function_name = function_dir.name
                sequence_file = function_dir / "sequence-diagram-en.md"
                overview_file = function_dir / "function-overview-en.md"
                
                total_flows = 0
                
                # Process sequence diagram file (detailed flows)
                if sequence_file.exists():
                    print(f"Processing function: {function_name}")
                    
                    # Extract flow entities from sequence diagram
                    flow_entities = self.process_sequence_diagram(function_name, sequence_file)
                    self.entities.extend(flow_entities)
                    
                    # Create relationships
                    for entity in flow_entities:
                        relationship = {
                            "source": entity["id"],
                            "target": entity["parent_function"],
                            "relationship_type": "BELONGS_TO",
                            "description": f"{entity['name']} belongs to {function_name} function"
                        }
                        self.relationships.append(relationship)
                    
                    total_flows += len(flow_entities)
                    print(f"  - Extracted {len(flow_entities)} detailed flow entities")
                
                # Process function overview file (high-level process flow)
                if overview_file.exists():
                    if not sequence_file.exists():
                        print(f"Processing function: {function_name}")
                    
                    # Extract process flow from overview
                    overview_flows = self.process_function_overview(function_name, overview_file)
                    self.entities.extend(overview_flows)
                    
                    # Create relationships
                    for entity in overview_flows:
                        relationship = {
                            "source": entity["id"],
                            "target": entity["parent_function"],
                            "relationship_type": "BELONGS_TO",
                            "description": f"{entity['name']} belongs to {function_name} function"
                        }
                        self.relationships.append(relationship)
                    
                    total_flows += len(overview_flows)
                    if overview_flows:
                        print(f"  - Extracted {len(overview_flows)} process flow overview")
                
                if total_flows > 0:
                    print(f"  - Total: {total_flows} flow entities")
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the processed results.
        
        Returns:
            Dictionary containing entities and relationships
        """
        return {
            "entities": self.entities,
            "relationships": self.relationships,
            "metadata": {
                "module": self.module_name,
                "total_entities": len(self.entities),
                "total_relationships": len(self.relationships),
                "functions_processed": len(set(e["function_name"] for e in self.entities))
            }
        }
    
    def save_to_json(self, output_path: str) -> None:
        """
        Save the processed results to a JSON file.
        
        Args:
            output_path: Path to save the JSON file
        """
        results = self.get_results()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {output_path}")
        print(f"Total entities: {results['metadata']['total_entities']}")
        print(f"Total relationships: {results['metadata']['total_relationships']}")
        print(f"Functions processed: {results['metadata']['functions_processed']}")


def main():
    """
    Main function to demonstrate usage.
    """
    # Set up paths
    base_path = "/data_hdd_16t/vuongchu/nxGREG/ctc-data-en"
    module = "housing"
    output_path = f"/data_hdd_16t/vuongchu/nxGREG/json/{module}/{module}-flow-entities.json"
    
    # Create processor
    processor = FlowEntityProcessor(base_path, module_name=module)
    
    # Process all functions
    print("Starting flow entity extraction...\n")
    processor.process_all_functions()
    
    # Save results
    processor.save_to_json(output_path)
    
    # Print sample entity
    results = processor.get_results()
    if results['entities']:
        print("\n--- Sample Entity ---")
        print(json.dumps(results['entities'][0], indent=2))


if __name__ == "__main__":
    main()
