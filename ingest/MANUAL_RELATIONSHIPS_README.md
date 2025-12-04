# Manual Relationship Creation

This module provides functionality to manually create relationships between entities that may not be automatically detected during the extraction process.

## Overview

The `manual_creation.py` module allows you to:
- Create relationships between forms and form fields
- Create relationships between entities and their parent modules
- Compose multiple relationship creation tasks
- Apply selective relationship tasks

## Files

- **`ingest/manual_creation.py`**: Core module with relationship creation functions
- **`ingest/example_manual_usage.py`**: Examples demonstrating various usage patterns
- **`test_manual_relationships.py`**: Test script to verify functionality

## Usage

### 1. Basic Usage with Compose Function

The simplest way to create all manual relationships:

```python
from pathlib import Path
from core import GraphData
from ingest.manual_creation import compose_manual_tasks

# Create graph
graph = GraphData()

# Apply all manual relationship tasks
json_file = Path("json/contract-list-entities.json")
results = compose_manual_tasks(json_file, graph)

print(f"Created {sum(results.values())} relationships")
```

### 2. Selective Task Execution

Run only specific relationship creation tasks:

```python
from ingest.manual_creation import apply_manual_tasks_to_pipeline

# Run only form-field relationships
results = apply_manual_tasks_to_pipeline(
    json_file,
    graph,
    task_names=["form_field"]  # Available: "form_field", "parent_module"
)
```

### 3. Individual Function Calls

Call specific relationship creation functions directly:

```python
from ingest.manual_creation import (
    create_form_field_relationships,
    create_parent_module_relationships
)

# Create only form-field relationships
count = create_form_field_relationships(json_file, graph)
print(f"Created {count} form-field relationships")

# Create only parent-module relationships
count = create_parent_module_relationships(json_file, graph)
print(f"Created {count} parent-module relationships")
```

## Integration with Pipeline

The manual relationship creation is integrated into the `JSONToGraphPipeline` class in `ingest/json_to_graph.py`.

### Automatic Integration

By default, manual relationships are created automatically when you run the pipeline:

```python
from ingest.json_to_graph import JSONToGraphPipeline

pipeline = JSONToGraphPipeline(
    json_dir="json",
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

# Manual relationships are applied automatically
pipeline.run(wipe=True, apply_manual_relationships=True)
```

### Disabling Manual Relationships

To disable manual relationship creation:

```python
pipeline.run(wipe=True, apply_manual_relationships=False)
```

## Available Relationship Tasks

### 1. Form-Field Relationships

Creates `HAS_FIELD` relationships between forms and their fields.

**Matching Logic:**
- Finds all entities with `type="form"`
- Finds all entities with `type="form_field"`
- Matches when `form_field.form_id == form.form_id`

**Example:**
```json
Form: {
  "id": "form:anken_card_form",
  "type": "form",
  "form_id": "anken_cardForm"
}

FormField: {
  "id": "form_field:anken_no",
  "type": "form_field",
  "form_id": "anken_cardForm",  // Matches above
  "field_name": "ankenNo"
}

// Creates: form:anken_card_form -[HAS_FIELD]-> form_field:anken_no
```

### 2. Parent-Module Relationships

Creates `BELONGS_TO` relationships between entities and their parent modules.

**Matching Logic:**
- For any entity with a `parent_module` field
- Creates relationship: `entity -[BELONGS_TO]-> parent_module`

**Example:**
```json
Entity: {
  "id": "screen:contract_list_main",
  "type": "screen",
  "parent_module": "module:contract_list"
}

// Creates: screen:contract_list_main -[BELONGS_TO]-> module:contract_list
```

## Adding New Relationship Tasks

To add a new relationship creation task:

1. **Create the function** in `manual_creation.py`:

```python
def create_your_new_relationships(
    json_file_path: str | Path,
    graph: GraphData
) -> int:
    """
    Create your custom relationships.
    
    Returns:
        Number of relationships created
    """
    # Your logic here
    pass
```

2. **Add to `available_tasks`** in `apply_manual_tasks_to_pipeline`:

```python
available_tasks = {
    "form_field": create_form_field_relationships,
    "parent_module": create_parent_module_relationships,
    "your_task": create_your_new_relationships,  # Add here
}
```

3. **Add to `compose_manual_tasks`**:

```python
def compose_manual_tasks(json_file_path, graph):
    results = {}
    
    # Existing tasks...
    results["form_field_relationships"] = create_form_field_relationships(json_path, graph)
    results["parent_module_relationships"] = create_parent_module_relationships(json_path, graph)
    
    # Add your task
    results["your_task_relationships"] = create_your_new_relationships(json_path, graph)
    
    return results
```

## Testing

Run the test script to verify functionality:

```bash
python test_manual_relationships.py
```

Expected output:
```
Testing manual relationship creation...

INFO: Starting manual relationship creation...
INFO: Task 1: Creating form-field relationships...
INFO: Found 3 forms and 19 form fields
INFO: Created 19 form-field relationships
INFO: Task 2: Creating parent-module relationships...
INFO: Created 53 parent-module relationships

Total relationships created: 72
✓ Test completed successfully!
```

## Examples

Run the example script for various usage patterns:

```bash
cd ingest
python example_manual_usage.py
```

This demonstrates:
- Basic usage with compose_manual_tasks
- Selective task execution
- Individual function calls
- Relationship inspection

## API Reference

### `create_form_field_relationships(json_file_path, graph)`

Creates HAS_FIELD relationships between forms and form fields.

**Parameters:**
- `json_file_path` (str | Path): Path to JSON file with entities
- `graph` (GraphData): Graph object to add relationships to

**Returns:**
- `int`: Number of relationships created

### `create_parent_module_relationships(json_file_path, graph)`

Creates BELONGS_TO relationships between entities and parent modules.

**Parameters:**
- `json_file_path` (str | Path): Path to JSON file with entities
- `graph` (GraphData): Graph object to add relationships to

**Returns:**
- `int`: Number of relationships created

### `compose_manual_tasks(json_file_path, graph)`

Executes all manual relationship creation tasks.

**Parameters:**
- `json_file_path` (str | Path): Path to JSON file with entities
- `graph` (GraphData): Graph object to add relationships to

**Returns:**
- `Dict[str, int]`: Mapping of task names to relationship counts

### `apply_manual_tasks_to_pipeline(json_file_path, graph, task_names=None)`

Selectively applies manual relationship tasks.

**Parameters:**
- `json_file_path` (str | Path): Path to JSON file with entities
- `graph` (GraphData): Graph object to add relationships to
- `task_names` (List[str] | None): List of task names to execute. If None, executes all tasks.

**Returns:**
- `Dict[str, int]`: Mapping of task names to relationship counts

## Troubleshooting

### Issue: No relationships created

**Check:**
1. JSON file contains entities with correct types (`form`, `form_field`)
2. Form fields have `form_id` that matches a form's `form_id`
3. File path is correct

### Issue: AttributeError on GraphData

**Solution:** Ensure you're using the correct method names:
- Use `graph.add_relationship()` not `graph.add_edge()`
- Parameters: `start_key`, `end_key`, `rel_type`

### Issue: Relationships not appearing in Neo4j

**Check:**
1. Manual relationships are applied BEFORE `load_to_neo4j()`
2. Pipeline is configured with `apply_manual_relationships=True`
3. Nodes exist in the graph before creating relationships

## Performance

- **Form-Field Matching**: O(n) where n is the number of form fields
- **Parent-Module Matching**: O(n) where n is the number of entities
- **Memory**: Loads entire JSON file into memory

For large files (>100MB), consider:
- Processing in batches
- Streaming JSON parsing
- Database-side relationship creation
