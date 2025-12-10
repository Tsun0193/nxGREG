"""
Example usage of TabDescriptionProcessor

This script demonstrates how to use the TabDescriptionProcessor to extract
entities from tab description files.
"""

from process.tab_description_processor import TabDescriptionProcessor
from pathlib import Path
import json


def test_single_file():
    """Test processing a single description file."""
    print("=" * 80)
    print("Testing Single File Processing")
    print("=" * 80)
    
    processor = TabDescriptionProcessor("ctc-data-en", "simple")
    
    # Process the accounting tab description file
    file_path = Path("ctc-data-en/simple/accounting-info-simple-contract/description_accounting_init_screen-en.md")
    
    if file_path.exists():
        result = processor.process_file(file_path)
        
        print(f"\nFile: {result['file_path']}")
        print(f"Tab Name: {result['tab_name']}")
        print(f"\nEntities Found: {len(result['entities'])}")
        
        for entity in result['entities']:
            print(f"\n  - {entity['type']}: {entity['name']}")
            print(f"    ID: {entity['id']}")
            if entity['type'] == 'TabOverview':
                print(f"    Main Function: {entity['main_function']}")
                print(f"    Contract Type: {entity['contract_type']}")
            elif entity['type'] == 'TabProcessingFlow':
                print(f"    Has Mermaid Diagram: {bool(entity['mermaid_diagram'])}")
            elif entity['type'] == 'TabImpact':
                print(f"    Change Type: {entity['change_type']}")
                print(f"    Database Impact: {entity['database_impact'][:60]}...")
        
        print(f"\nRelationships Found: {len(result['relationships'])}")
        for rel in result['relationships']:
            print(f"  - {rel['from']} --[{rel['type']}]--> {rel['to']}")
    else:
        print(f"File not found: {file_path}")


def test_all_files():
    """Test processing all description files in simple module."""
    print("\n" + "=" * 80)
    print("Testing All Files Processing (Simple Module)")
    print("=" * 80)
    
    processor = TabDescriptionProcessor("ctc-data-en", "simple")
    results = processor.process_all_files()
    
    print(f"\nModule: {results['module']}")
    print(f"Total Files: {results['total_files']}")
    print(f"Total Entities: {results['total_entities']}")
    print(f"Total Relationships: {results['total_relationships']}")
    
    # Group entities by type
    entity_types = {}
    for entity in results['entities']:
        entity_type = entity['type']
        if entity_type not in entity_types:
            entity_types[entity_type] = []
        entity_types[entity_type].append(entity)
    
    print("\nEntities by Type:")
    for entity_type, entities in entity_types.items():
        print(f"  - {entity_type}: {len(entities)}")
        for entity in entities[:3]:  # Show first 3
            print(f"    • {entity['name']}")
        if len(entities) > 3:
            print(f"    ... and {len(entities) - 3} more")
    
    # Save to JSON
    output_path = "json/simple-tab-descriptions.json"
    processor.save_to_json(output_path)


def test_housing_module():
    """Test processing housing module (if exists)."""
    print("\n" + "=" * 80)
    print("Testing Housing Module")
    print("=" * 80)
    
    housing_path = Path("ctc-data-en/housing")
    if not housing_path.exists():
        print("Housing module not found, skipping...")
        return
    
    processor = TabDescriptionProcessor("ctc-data-en", "housing")
    description_files = processor.find_description_files()
    
    if not description_files:
        print("No description files found in housing module")
        return
    
    print(f"Found {len(description_files)} description files:")
    for file_path in description_files:
        print(f"  - {file_path.relative_to(Path('ctc-data-en'))}")
    
    results = processor.process_all_files()
    print(f"\nTotal Entities: {results['total_entities']}")
    print(f"Total Relationships: {results['total_relationships']}")
    
    # Save to JSON
    output_path = "json/housing-tab-descriptions.json"
    processor.save_to_json(output_path)


def display_sample_entity():
    """Display a sample entity in detail."""
    print("\n" + "=" * 80)
    print("Sample Entity (Accounting Tab Overview)")
    print("=" * 80)
    
    processor = TabDescriptionProcessor("ctc-data-en", "simple")
    file_path = Path("ctc-data-en/simple/accounting-info-simple-contract/description_accounting_init_screen-en.md")
    
    if file_path.exists():
        result = processor.process_file(file_path)
        overview_entity = next((e for e in result['entities'] if e['type'] == 'TabOverview'), None)
        
        if overview_entity:
            print(json.dumps(overview_entity, indent=2, ensure_ascii=False))


def main():
    """Run all tests."""
    # Test single file
    # test_single_file()
    
    # Test all files in simple module
    test_all_files()
    
    # Test housing module
    # test_housing_module()
    
    # Display sample entity
    # display_sample_entity()


if __name__ == "__main__":
    main()
