"""
Flow Entity Processor

This module processes sequence diagram markdown files from function directories
and extracts flow entities with their mermaid diagrams. It also creates relationships
between flow entities and their parent functions.

Author: System
Date: December 8, 2025
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class FlowEntityProcessor:
    """
    Processes sequence diagram files to extract flow entities and establish
    relationships with functions.
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
        self.module_path = self.base_path / module_name / "yuusyou-kihon" / "functions"
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
                    "type": "ProcessFlow",
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
    
    def process_all_functions(self) -> None:
        """
        Process all function directories and extract flow entities.
        """
        if not self.module_path.exists():
            raise FileNotFoundError(f"Module path not found: {self.module_path}")
        
        # Iterate through function directories
        for function_dir in self.module_path.iterdir():
            if function_dir.is_dir():
                function_name = function_dir.name
                sequence_file = function_dir / "sequence-diagram-en.md"
                
                if sequence_file.exists():
                    print(f"Processing function: {function_name}")
                    
                    # Extract flow entities
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
                    
                    print(f"  - Extracted {len(flow_entities)} flow entities")
    
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
    output_path = "/data_hdd_16t/vuongchu/nxGREG/json/simple-flow-entities.json"
    
    # Create processor
    processor = FlowEntityProcessor(base_path, module_name="simple")
    
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
