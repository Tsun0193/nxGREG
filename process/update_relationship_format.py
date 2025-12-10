"""
Script to update relationship format in all JSON files from old format (from/to/type) 
to new format (source/target/relationship_type)
"""

import json
from pathlib import Path


def update_relationship_format(relationship):
    """Convert old format to new format."""
    if "from" in relationship:
        relationship["source"] = relationship.pop("from")
    if "to" in relationship:
        relationship["target"] = relationship.pop("to")
    if "type" in relationship and "relationship_type" not in relationship:
        relationship["relationship_type"] = relationship.pop("type")
    return relationship


def update_json_file(file_path):
    """Update relationships in a JSON file."""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update relationships if they exist
    if "relationships" in data:
        updated_count = 0
        for relationship in data["relationships"]:
            if "from" in relationship or "to" in relationship:
                update_relationship_format(relationship)
                updated_count += 1
        
        print(f"  Updated {updated_count} relationships")
        
        # Save updated JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Saved updated file")
    else:
        print(f"  No relationships found")


def main():
    """Process all JSON files."""
    json_dir = Path("json")
    
    # Find all JSON files
    json_files = list(json_dir.rglob("*.json"))
    
    print(f"Found {len(json_files)} JSON files\n")
    
    for json_file in json_files:
        try:
            update_json_file(json_file)
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()
    
    print("Done!")


if __name__ == "__main__":
    main()
