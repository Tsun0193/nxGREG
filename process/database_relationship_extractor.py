"""
Database Relationship Extractor

This module processes function overview markdown files and extracts database table
relationships. It creates relationships between functions and database tables based
on CRUD operations (Create, Read, Update, Delete).

Author: System
Date: December 8, 2025
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import pandas as pd
import io


class DatabaseRelationshipExtractor:
    """
    Extracts database table relationships from function overview files.
    """
    
    def __init__(self, base_path: str, module_name: str = "simple"):
        """
        Initialize the extractor.
        
        Args:
            base_path: Base path to the ctc-data-en directory
            module_name: Module name (default: "simple")
        """
        self.base_path = Path(base_path)
        self.module_name = module_name
        self.module_path = self.base_path / module_name / "yuusyou-kihon" / "functions"
        self.relationships = []
    

    def extract_database_tables(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract database table information from function overview markdown using DataFrame.
        
        Args:
            file_path: Path to the function-overview-en.md file
            
        Returns:
            List of table relationships with operations
        """
        tables = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the section "4.2. Database Tables Used"
        section_pattern = r'###\s+4\.2\.\s+Database Tables Used(.*?)(?=\n#{1,3}\s+|\*\*Notes:\*\*|\Z)'
        section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not section_match:
            return tables
        
        section_content = section_match.group(1)
        
        # Find the table within the section (starts with | Table Name |)
        table_start = -1
        lines = section_content.splitlines()
        for i, line in enumerate(lines):
            if '| Table Name |' in line or '|Table Name|' in line:
                table_start = i
                break
        
        if table_start == -1:
            return tables
        
        # Extract only the table portion
        table_lines = lines[table_start:]
        table_content = '\n'.join(table_lines)
        
        # Remove the separator row (the --- row)
        clean_md = "\n".join(
            line for line in table_content.splitlines()
            if not set(line.strip()) == {"|", "-", " "}
        )

        try:
            # Read as pipe-separated
            df = pd.read_csv(io.StringIO(clean_md), sep="|", engine="python")

            # Clean column names (strip whitespace)
            df.columns = df.columns.str.strip()
            
            # Drop completely empty columns
            df = df.dropna(axis=1, how='all')
            
            # Strip whitespace from all string columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
            
            # Remove rows where Table Name is empty or NaN
            df = df[df['Table Name'].notna() & (df['Table Name'] != '')]
            
            # Expected columns
            expected_cols = ['Table Name', 'Description', 'Create', 'Read', 'Update', 'Delete']
            
            # Check if we have the required columns
            if 'Table Name' not in df.columns or 'Description' not in df.columns:
                return tables
            
            # Process each row
            for idx, row in df.iterrows():
                table_name = str(row['Table Name']).strip('*').strip()
                
                # Skip if table name is empty, is the header, or is separator dashes
                if (not table_name 
                    or table_name.lower() == 'table name'
                    or set(table_name) <= {'-', ' '}):
                    continue
                
                description = str(row.get('Description', ''))
                
                # Determine operations by checking if column values are non-empty
                operations = set()
                
                # Check each CRUD column - if it has any non-whitespace content, count it as that operation
                if 'Create' in df.columns and pd.notna(row.get('Create')) and str(row.get('Create', '')).strip():
                    operations.add('create')
                if 'Read' in df.columns and pd.notna(row.get('Read')) and str(row.get('Read', '')).strip():
                    operations.add('read')
                if 'Update' in df.columns and pd.notna(row.get('Update')) and str(row.get('Update', '')).strip():
                    operations.add('update')
                if 'Delete' in df.columns and pd.notna(row.get('Delete')) and str(row.get('Delete', '')).strip():
                    operations.add('delete')
                
                # Only add if there are operations
                if operations:
                    tables.append({
                        'table_name': table_name,
                        'description': description,
                        'operations': operations
                    })
        
        except Exception as e:
            print(f"    WARNING: Error parsing table: {e}")
            return tables
        
        return tables
    
    def create_relationships(self, function_name: str, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create relationships between function and database tables.
        
        Args:
            function_name: Name of the function
            tables: List of table information with operations
            
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        for table_info in tables:
            # Convert operations set to comma-separated string
            operation_type = ','.join(sorted(table_info['operations']))
            
            relationship = {
                'source': f'function:{function_name}',
                'target': f'database_table:{table_info["table_name"]}',
                'relationship_type': 'uses_table',
                'operation_type': operation_type,
                'table_description': table_info['description']
            }
            
            relationships.append(relationship)
        
        return relationships
    
    def process_function_overview(self, function_name: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single function overview file and extract database relationships.
        
        Args:
            function_name: Name of the function
            file_path: Path to the function-overview-en.md file
            
        Returns:
            List of relationships extracted from the file
        """
        # Extract database tables
        tables = self.extract_database_tables(file_path)
        
        # Create relationships
        relationships = self.create_relationships(function_name, tables)
        
        return relationships
    
    def process_all_functions(self) -> None:
        """
        Process all function directories and extract database relationships.
        """
        if not self.module_path.exists():
            raise FileNotFoundError(f"Module path not found: {self.module_path}")
        
        # Iterate through function directories
        for function_dir in self.module_path.iterdir():
            if function_dir.is_dir():
                function_name = function_dir.name
                overview_file = function_dir / "function-overview-en.md"
                
                if overview_file.exists():
                    print(f"Processing function: {function_name}")
                    
                    # Extract relationships
                    relationships = self.process_function_overview(function_name, overview_file)
                    self.relationships.extend(relationships)
                    
                    print(f"  - Extracted {len(relationships)} database relationships")
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the processed results.
        
        Returns:
            Dictionary containing relationships and metadata
        """
        # Get unique tables and functions
        unique_tables = set(r['target'] for r in self.relationships)
        unique_functions = set(r['source'] for r in self.relationships)
        
        return {
            'relationships': self.relationships,
            'metadata': {
                'module': self.module_name,
                'total_relationships': len(self.relationships),
                'unique_functions': len(unique_functions),
                'unique_tables': len(unique_tables)
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
        print(f"Total relationships: {results['metadata']['total_relationships']}")
        print(f"Unique functions: {results['metadata']['unique_functions']}")
        print(f"Unique tables: {results['metadata']['unique_tables']}")


def main():
    """
    Main function to demonstrate usage.
    """
    # Set up paths
    base_path = "/data_hdd_16t/vuongchu/nxGREG/ctc-data-en"
    output_path = "/data_hdd_16t/vuongchu/nxGREG/json/simple-database-relationships.json"
    
    # Create extractor
    extractor = DatabaseRelationshipExtractor(base_path, module_name="simple")
    
    # Process all functions
    print("Starting database relationship extraction...\n")
    extractor.process_all_functions()
    
    # Save results
    extractor.save_to_json(output_path)
    
    # Print sample relationships
    results = extractor.get_results()
    if results['relationships']:
        print("\n--- Sample Relationships ---")
        for rel in results['relationships'][:3]:
            print(json.dumps(rel, indent=2))


if __name__ == "__main__":
    main()
