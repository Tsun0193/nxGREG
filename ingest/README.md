# Ingest Module

Pipeline for loading JSON entities and relationships into Neo4j graph database.

## Features

- **Mixed Mode**: Automatically detects and loads both entities and relationships from any JSON file
- **Flexible Format Support**: Handles multiple JSON structures
- **Batch Processing**: Loads all JSON files from a directory
- **Graph Database Integration**: Uses existing Neo4j loader and GraphData classes

## Supported JSON Formats

### 1. Entities Only (List)
```json
[
  {
    "id": "entity_1",
    "type": "entity_type",
    "name": "Entity Name",
    "properties": {...}
  }
]
```

### 2. Relationships Only (Object)
```json
{
  "relationships": [
    {
      "source": "entity_1",
      "target": "entity_2",
      "relationship_type": "RELATES_TO",
      "properties": {...}
    }
  ]
}
```

### 3. Mixed Format (Both Entities and Relationships)
```json
{
  "entities": [
    {
      "id": "entity_1",
      "type": "entity_type",
      "name": "Entity Name"
    }
  ],
  "relationships": [
    {
      "source": "entity_1",
      "target": "entity_2",
      "relationship_type": "RELATES_TO"
    }
  ]
}
```

## Usage

### Quick Start

```python
from ingest import JSONToGraphPipeline

pipeline = JSONToGraphPipeline(
    json_dir="json/",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

try:
    # Load all JSON files with auto-detection
    pipeline.run(wipe=True, use_mixed_mode=True)
finally:
    pipeline.close()
```

### Run from Command Line

```bash
# Using environment variables
export NEO4J_URL="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your_password"

python -m ingest.json_to_graph
```

### Advanced Usage

```python
# Load specific files manually
pipeline.load_from_mixed_file("json/my-data.json")
pipeline.load_entities_from_file("json/entities.json")
pipeline.load_relationships_from_file("json/relationships.json")
pipeline.load_to_neo4j(wipe=False)

# Use custom filename patterns (legacy mode)
pipeline.run(
    entity_patterns=["entities_v4", "components"],
    relationship_patterns=["cross-layer", "database"],
    wipe=True,
    use_mixed_mode=False
)
```

## Configuration

Set these environment variables or pass them to the constructor:

- `NEO4J_URL`: Neo4j connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USERNAME`: Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password (default: `password`)

## API Reference

### JSONToGraphPipeline

#### Methods

- `load_entities_from_file(file_path)`: Load entities from a JSON file
- `load_relationships_from_file(file_path)`: Load relationships from a JSON file
- `load_from_mixed_file(file_path)`: Load both entities and relationships from a single file
- `load_all_json_files(entity_patterns, relationship_patterns, use_mixed_mode)`: Load all JSON files
- `load_to_neo4j(wipe)`: Push loaded data to Neo4j
- `run(entity_patterns, relationship_patterns, wipe, use_mixed_mode)`: Run complete pipeline
- `close()`: Close Neo4j connection

#### Parameters

- `wipe`: If `True`, clears all existing data in Neo4j before loading (default: `False`)
- `use_mixed_mode`: If `True`, auto-detects content in all JSON files (default: `True`)
- `entity_patterns`: List of filename patterns for entity files (e.g., `["entities", "component"]`)
- `relationship_patterns`: List of filename patterns for relationship files (e.g., `["relationships"]`)

## Examples

See `example_usage.py` for complete examples.
