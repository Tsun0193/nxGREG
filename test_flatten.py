"""Test script to verify property flattening."""

import json
from ingest.json_to_graph import JSONToGraphPipeline

# Test data
test_entity = {
    "id": "screen:contract_type_selection",
    "type": "screen",
    "name": "Contract Type Selection Screen",
    "parent_module": "module:contract_list",
    "properties": {
        "screen_id": "GCNT90xxx",
        "title": "Contract Type Selection",
        "url_pattern": "/dsmart/contract/keiyakuList/keiyakuListAssign.do",
        "nested": {
            "level2": "value"
        },
        "array": ["item1", "item2"]
    },
    "metadata": {
        "source_file": "ctc-data-en/contract-list/screen-flow-en.md"
    }
}

print("Original entity:")
print(json.dumps(test_entity, indent=2))
print("\n" + "="*80 + "\n")

# Extract raw properties (everything except id and type)
raw_properties = {k: v for k, v in test_entity.items() if k not in ["id", "type"]}
print("Raw properties:")
print(json.dumps(raw_properties, indent=2))
print("\n" + "="*80 + "\n")

# Flatten
flattened = JSONToGraphPipeline._flatten_properties(raw_properties)
print("Flattened properties:")
print(json.dumps(flattened, indent=2, ensure_ascii=False))
print("\n" + "="*80 + "\n")

# Sanitize
sanitized = JSONToGraphPipeline._sanitize_properties(flattened)
print("Sanitized properties:")
print(json.dumps(sanitized, indent=2, ensure_ascii=False))
print("\n" + "="*80 + "\n")

# Check types
print("Type check:")
for key, value in sanitized.items():
    print(f"  {key}: {type(value).__name__} = {repr(value)}")
