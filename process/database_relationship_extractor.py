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
    
    def __init__(self, base_path: str, module_name: str = "simple", screen: str = "yuusyou-kihon"):
        """
        Initialize the extractor.
        
        Args:
            base_path: Base path to the ctc-data-en directory
            module_name: Module name (default: "simple")
        """
        self.base_path = Path(base_path)
        self.module_name = module_name
        self.module_path = self.base_path / module_name / screen / "functions"
        self.relationships = []
        self.entities = []  # Store database table entities
        self.seen_tables = set()  # Track unique tables
    

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
    
    def determine_table_type(self, table_name: str) -> str:
        """
        Determine table type based on prefix.
        
        Args:
            table_name: Name of the database table
            
        Returns:
            Table type (master, transaction, view, sequence, index, or unknown)
        """
        table_upper = table_name.upper()
        
        if table_upper.startswith('M_'):
            return 'master'
        elif table_upper.startswith('T_'):
            return 'transaction'
        elif table_upper.startswith('V_'):
            return 'view'
        elif table_upper.startswith('S_'):
            return 'sequence'
        elif table_upper.startswith('IDX_'):
            return 'index'
        else:
            return 'unknown'
    
    def create_database_entity(self, table_name: str, description: str, source_file: str) -> Dict[str, Any]:
        """
        Create a database table entity.
        
        Args:
            table_name: Name of the database table
            description: Description of the table
            source_file: Source file path where the table was found
            
        Returns:
            Database entity dictionary
        """
        table_type = self.determine_table_type(table_name)
        
        # Generate a readable name from table name
        # Remove prefix and convert underscores to spaces, then title case
        name_without_prefix = table_name
        for prefix in ['m_', 't_', 'v_', 's_', 'idx_']:
            if table_name.lower().startswith(prefix):
                name_without_prefix = table_name[len(prefix):]
                break
        
        readable_name = ' '.join(word.capitalize() for word in name_without_prefix.split('_'))
        if table_type == 'master':
            readable_name += ' Master Table'
        elif table_type == 'transaction':
            readable_name += ' Transaction Table'
        elif table_type == 'view':
            readable_name += ' View'
        elif table_type == 'sequence':
            readable_name += ' Sequence'
        elif table_type == 'index':
            readable_name += ' Index'
        else:
            readable_name += ' Table'
        
        entity = {
            'id': f'database_table:{table_name}',
            'type': 'database_table',
            'name': readable_name,
            'table_name': table_name,
            'table_type': table_type,
            'description': description if description else f'{readable_name}',
            'source_file': source_file
        }
        
        return entity
    
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
        # Convert function name from hyphen-separated to underscore-separated
        function_name_normalized = function_name.replace('-', '_')
        
        # Extract database tables
        tables = self.extract_database_tables(file_path)
        
        # Create database entities for unique tables
        relative_path = str(file_path.relative_to(self.base_path.parent))
        for table_info in tables:
            table_name = table_info['table_name']
            if table_name not in self.seen_tables:
                entity = self.create_database_entity(
                    table_name=table_name,
                    description=table_info['description'],
                    source_file=relative_path
                )
                self.entities.append(entity)
                self.seen_tables.add(table_name)
        
        # Create relationships
        relationships = self.create_relationships(function_name_normalized, tables)
        
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
            Dictionary containing entities, relationships and metadata
        """
        # Get unique tables and functions
        unique_tables = set(r['target'] for r in self.relationships)
        unique_functions = set(r['source'] for r in self.relationships)
        
        # Count entities by type
        entity_type_counts = {}
        for entity in self.entities:
            table_type = entity['table_type']
            entity_type_counts[table_type] = entity_type_counts.get(table_type, 0) + 1
        
        return {
            'entities': self.entities,
            'relationships': self.relationships,
            'metadata': {
                'module': self.module_name,
                'total_entities': len(self.entities),
                'total_relationships': len(self.relationships),
                'unique_functions': len(unique_functions),
                'unique_tables': len(unique_tables),
                'entity_type_counts': entity_type_counts
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
        print(f"Unique functions: {results['metadata']['unique_functions']}")
        print(f"Unique tables: {results['metadata']['unique_tables']}")
        print(f"\nEntity breakdown by type:")
        for table_type, count in results['metadata']['entity_type_counts'].items():
            print(f"  - {table_type}: {count}")


def main():
    """
    Main function to demonstrate usage.
    """
    # Set up paths
    base_path = "/data_hdd_16t/vuongchu/nxGREG/ctc-data-en"
    output_path = "/data_hdd_16t/vuongchu/nxGREG/json/simple/simple-database-relationships.json"
    
    # Create extractor
    extractor = DatabaseRelationshipExtractor(base_path, module_name="simple")
    
    # Process all functions
    print("Starting database relationship extraction...\n")
    extractor.process_all_functions()
    
    # Save results
    extractor.save_to_json(output_path)
    
    # Print sample entities and relationships
    results = extractor.get_results()
    if results['entities']:
        print("\n--- Sample Entities ---")
        for entity in results['entities'][:3]:
            print(json.dumps(entity, indent=2))
    
    if results['relationships']:
        print("\n--- Sample Relationships ---")
        for rel in results['relationships'][:3]:
            print(json.dumps(rel, indent=2))


if __name__ == "__main__":
    main()
