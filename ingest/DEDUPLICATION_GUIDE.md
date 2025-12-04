# Entity Deduplication Guide

## Overview

The `EntityDeduplicator` class helps manage duplicate entities across multiple JSON files before loading them into Neo4j. It intelligently detects and merges duplicate entities while preserving valuable properties from all sources.

### Problem Statement

When working with entities from multiple JSON files:
- Same entities may exist with different IDs (e.g., `database_table:anken` vs `database_table:t_anken`)
- Entities from different sources may contain complementary properties
- Loading without deduplication creates redundant nodes in the graph
- Properties from one source might be more complete than another

### Solution

The deduplicator:
1. **Detects duplicates** by multiple criteria:
   - Exact ID match
   - `table_name` match (for database tables)
   - Name similarity (for general lookup)

2. **Merges intelligently**:
   - Keeps the first ID encountered
   - Adds missing properties from duplicate sources
   - Preserves existing values if they're more complete
   - Tracks all source files contributing to merged entities

3. **Reports changes**:
   - Merge history showing what was merged and why
   - Statistics on merged vs new entities
   - Detailed per-entity merge tracking

## Quick Start

### Basic Usage

```python
from ingest.entity_deduplicator import EntityDeduplicator
from pathlib import Path

# Initialize
dedup = EntityDeduplicator()

# Load entities from multiple files
json_dir = Path("json")
files = list(json_dir.glob("*.json"))

dedup.load_from_multiple_files(
    files,
    priority_order=["database-entities", "component-entities"]  # Optional priority
)

# Get results
entities = dedup.get_all_entities()
report = dedup.get_merge_report()

# Export
dedup.export_deduplicated_entities(Path("output/entities.json"))
dedup.export_merge_report(Path("output/merge_report.json"))
```

### With Neo4j Pipeline

```python
from ingest.json_to_graph import JSONToGraphPipeline

# Create pipeline WITH deduplicator
pipeline = JSONToGraphPipeline(
    json_dir="json",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    use_deduplicator=True  # Enable deduplication
)

# Run - automatically deduplicates before loading
pipeline.run(wipe=True)

# View merge report
report = pipeline.deduplicator.get_merge_report()
print(f"Merged: {report['merged_entities']} entities")
```

## API Reference

### EntityDeduplicator

#### Methods

##### `add_entity(entity, source_file="unknown") -> Tuple[str, bool]`

Add an entity to the deduplicator.

**Parameters:**
- `entity` (dict): Entity with `id`, `type`, and other properties
- `source_file` (str): Source file name for tracking

**Returns:**
- `(entity_id, is_new)`: Entity ID and whether it's new (True) or merged (False)

**Example:**
```python
entity = {
    "id": "database_table:anken",
    "type": "database_table",
    "name": "Project Table",
    "table_name": "t_anken"
}

entity_id, is_new = dedup.add_entity(entity, "database_entities.json")
print(f"Entity ID: {entity_id}, New: {is_new}")
```

##### `load_from_file(file_path, source_label=None) -> int`

Load entities from a single JSON file.

**Parameters:**
- `file_path` (Path): Path to JSON file
- `source_label` (str): Optional custom label for source

**Returns:**
- Number of new entities added

**Example:**
```python
count = dedup.load_from_file(Path("json/entities.json"))
print(f"Added {count} new entities")
```

##### `load_from_multiple_files(file_paths, priority_order=None) -> Dict[str, int]`

Load entities from multiple files with optional priority ordering.

**Parameters:**
- `file_paths` (List[Path]): List of JSON file paths
- `priority_order` (List[str]): Optional patterns for priority (files with earlier patterns loaded first)

**Returns:**
- Dictionary mapping filename to count of new entities added

**Example:**
```python
files = [
    Path("json/database-entities-v2.json"),
    Path("json/component-entities-v3.json"),
    Path("json/cross-layer-relationships.json")
]

stats = dedup.load_from_multiple_files(
    files,
    priority_order=["database-entities", "component-entities"]
)

for filename, count in stats.items():
    print(f"{filename}: {count} new entities")
```

##### `get_all_entities() -> List[Dict]`

Get all deduplicated entities.

**Returns:**
- List of entity dictionaries

##### `get_entity_by_id(entity_id: str) -> Dict | None`

Get a specific entity by ID.

**Parameters:**
- `entity_id` (str): Entity ID

**Returns:**
- Entity dictionary or None if not found

##### `find_duplicates_by_type(entity_type: str) -> List[Tuple[str, List[str]]]`

Find potential duplicate entities by type and name.

**Parameters:**
- `entity_type` (str): Type of entities to check (e.g., "database_table")

**Returns:**
- List of `(name, [entity_ids])` tuples for entities with same name

**Example:**
```python
duplicates = dedup.find_duplicates_by_type("database_table")
for name, ids in duplicates:
    print(f"{name}: {ids}")
```

##### `get_merge_report() -> Dict[str, Any]`

Get comprehensive merge statistics and history.

**Returns:**
- Dictionary with:
  - `total_entities`: Total number of unique entities
  - `merged_entities`: Count of entities that received merged data
  - `new_entities`: Count of entities never merged
  - `merge_operations`: Total merge operations performed
  - `merge_history`: List of detailed merge records

**Example:**
```python
report = dedup.get_merge_report()
print(f"Total: {report['total_entities']}")
print(f"Merged: {report['merged_entities']}")
print(f"New: {report['new_entities']}")

for merge_op in report['merge_history'][:5]:
    print(f"\nMerge into {merge_op['target_id']}:")
    print(f"  Properties added: {merge_op['properties_added']}")
    print(f"  Properties updated: {merge_op['properties_updated']}")
```

##### `export_deduplicated_entities(output_file: Path) -> None`

Export deduplicated entities to JSON file.

**Parameters:**
- `output_file` (Path): Output file path

**Example:**
```python
dedup.export_deduplicated_entities(Path("output/entities.json"))
```

##### `export_merge_report(output_file: Path) -> None`

Export merge report to JSON file.

**Parameters:**
- `output_file` (Path): Output file path

**Example:**
```python
dedup.export_merge_report(Path("output/merge_report.json"))
```

## Merging Strategy

### How Duplicates Are Detected

1. **Exact ID Match**: If entity with same `id` already exists
   ```
   "id": "database_table:anken" → existing entity found → merge
   ```

2. **Table Name Match** (for database_table entities):
   ```
   Entity 1: id="database_table:anken", table_name="t_anken"
   Entity 2: id="database_table:t_anken", table_name="t_anken"
   → Same table_name → merge into Entity 1
   ```

3. **Priority Ordering**: Files loaded first take precedence
   ```
   Load order: ["database-entities-v2", "component-entities-v3"]
   
   database-entities-v2.json defines: id="database_table:anken"
   component-entities-v3.json also has: id="database_table:t_anken" (same table)
   
   Result: Both merged into first ID found (database_table:anken)
   ```

### Property Merge Logic

When merging an entity:

1. **Missing properties** → Added from new entity
2. **Existing empty properties** → Updated with non-empty value
3. **Conflicting non-empty values** → Keep existing, log difference
4. **Source file tracking** → Appended to `_source_files` list

**Example:**

```
Existing Entity:
{
  "id": "database_table:anken",
  "type": "database_table",
  "name": "Project Table",
  "table_name": "t_anken",
  "description": ""
}

New Entity (being merged):
{
  "id": "database_table:anken",
  "type": "database_table",
  "name": "T_ANKEN",
  "table_name": "t_anken",
  "description": "Main project table",
  "primary_key": "anken_no"
}

Result After Merge:
{
  "id": "database_table:anken",
  "type": "database_table",
  "name": "Project Table",  # Kept existing
  "table_name": "t_anken",
  "description": "Main project table",  # Updated from empty
  "primary_key": "anken_no",  # Added new property
  "_source_files": ["database-entities-v2.json", "component-entities-v3.json"]
}
```

## Examples

### Example 1: Deduplicate Without Neo4j

```python
from ingest.entity_deduplicator import EntityDeduplicator
from pathlib import Path

dedup = EntityDeduplicator()

# Load from multiple files
json_dir = Path("json")
dedup.load_from_file(json_dir / "database-entities-v2.json", "baseline")
dedup.load_from_file(json_dir / "component-entities-v3.json", "component")

# Export results
dedup.export_deduplicated_entities(Path("output/dedup_entities.json"))

# Print report
report = dedup.get_merge_report()
print(f"Deduplication complete:")
print(f"  Total entities: {report['total_entities']}")
print(f"  Merged: {report['merged_entities']}")
print(f"  New: {report['new_entities']}")
```

### Example 2: Find Duplicates

```python
# Show all potential database table duplicates
duplicates = dedup.find_duplicates_by_type("database_table")

if duplicates:
    print(f"Found {len(duplicates)} groups with duplicate names:")
    for name, ids in duplicates:
        print(f"\n{name}:")
        for eid in ids:
            entity = dedup.get_entity_by_id(eid)
            print(f"  - {eid}")
            print(f"    From: {entity.get('_source_files', [])}")
```

### Example 3: Custom Merging

```python
# You can add entities programmatically
entity1 = {
    "id": "database_table:customers",
    "type": "database_table",
    "name": "Customers",
    "table_name": "t_kokyaku"
}

entity2 = {
    "id": "database_table:kokyaku",
    "type": "database_table",
    "name": "Customers",  # Same logical entity
    "table_name": "t_kokyaku",  # Same table
    "description": "Customer master data"
}

# Add first
id1, new1 = dedup.add_entity(entity1, "source1.json")
print(f"Added: {id1} (new={new1})")

# Add second - will be merged into first
id2, new2 = dedup.add_entity(entity2, "source2.json")
print(f"Added: {id2} (new={new2})")  # new2 will be False

# Check merged entity
merged = dedup.get_entity_by_id(id1)
print(f"Merged entity sources: {merged['_source_files']}")
print(f"Description: {merged.get('description')}")
```

## Troubleshooting

### Entities Not Being Merged

**Issue**: Expected duplicates aren't being merged

**Solutions**:
1. Check that `id` fields match exactly (case-sensitive)
2. For database tables, verify `table_name` matches
3. Use `find_duplicates_by_type()` to see what exists
4. Check merge report for what was actually merged

### Lost Properties

**Issue**: Properties from one source are missing

**Solutions**:
1. Check load priority - files loaded first take precedence
2. Use `priority_order` parameter to control which file is loaded first:
   ```python
   dedup.load_from_multiple_files(
       files,
       priority_order=["database-entities"]  # Load this first
   )
   ```
3. Review merge report to see what properties were preserved/overridden

### Neo4j Integration Issues

**Issue**: Duplicates still appearing in Neo4j

**Solution**: Ensure deduplicator is enabled:
```python
pipeline = JSONToGraphPipeline(
    ...,
    use_deduplicator=True  # MUST be True
)
```

## Performance Considerations

- **Memory**: All entities kept in memory during deduplication
- **Files**: Can handle multiple JSON files efficiently
- **Large datasets**: For 10,000+ entities, consider batch processing

## Best Practices

1. **Use Priority Ordering**: Specify which files are authoritative
   ```python
   dedup.load_from_multiple_files(
       files,
       priority_order=["v2", "v3"]  # v2 is baseline
   )
   ```

2. **Review Reports**: Always check merge report
   ```python
   report = dedup.get_merge_report()
   if report['merged_entities'] > 0:
       # Review what was merged
   ```

3. **Export Results**: Keep deduplicated entities for reference
   ```python
   dedup.export_deduplicated_entities(Path("output/final_entities.json"))
   ```

4. **Validate in Neo4j**: Query to verify duplicates are gone
   ```cypher
   MATCH (n) WITH n.table_name as tn, count(*) as cnt
   WHERE cnt > 1
   RETURN tn, cnt
   ```

## Related Files

- `entity_deduplicator.py` - Main deduplication logic
- `json_to_graph.py` - Integration with Neo4j pipeline
- `example_deduplication.py` - Usage examples
