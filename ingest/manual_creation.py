"""
Manual creation of entities and relationships from JSON files.

This module provides functions to manually create relationships between entities
that may not be automatically detected during extraction.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

from core import GraphData

logger = logging.getLogger(__name__)


def create_form_field_relationships(
    json_file_path: str | Path,
    graph: GraphData
) -> int:
    """
    Create relationships between form and form_field entities.
    
    This function reads a JSON file, finds all form and form_field entities,
    and creates HAS_FIELD relationships when a form_field's form_id matches
    a form's form_id.
    
    Args:
        json_file_path: Path to the JSON file containing entities
        graph: GraphData object to add relationships to
        
    Returns:
        Number of relationships created
        
    Example:
        >>> graph = GraphData()
        >>> count = create_form_field_relationships("entities.json", graph)
        >>> print(f"Created {count} form-field relationships")
    """
    json_path = Path(json_file_path)
    
    if not json_path.exists():
        logger.error(f"JSON file not found: {json_path}")
        return 0
    
    # Read JSON file
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            entities = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file {json_path}: {e}")
        return 0
    except Exception as e:
        logger.error(f"Failed to read JSON file {json_path}: {e}")
        return 0
    
    if not isinstance(entities, list):
        logger.error(f"Expected a list of entities, got {type(entities)}")
        return 0
    
    # Separate forms and form fields
    forms: Dict[str, Dict[str, Any]] = {}
    form_fields: List[Dict[str, Any]] = []
    
    for entity in entities:
        if not isinstance(entity, dict):
            continue
            
        entity_id = entity.get("id", "")
        entity_type = entity.get("type", "")
        
        if entity_type == "form":
            form_id = entity.get("form_id")
            if form_id:
                forms[form_id] = entity
        elif entity_type == "form_field":
            form_fields.append(entity)
    
    logger.info(f"Found {len(forms)} forms and {len(form_fields)} form fields")
    
    # Create relationships
    relationships_created = 0
    
    for field in form_fields:
        field_id = field.get("id")
        field_form_id = field.get("form_id")
        
        if not field_id or not field_form_id:
            continue
        
        # Find matching form
        if field_form_id in forms:
            form = forms[field_form_id]
            form_entity_id = form.get("id")
            
            if form_entity_id:
                # Create relationship: Form -[HAS_FIELD]-> FormField
                graph.add_relationship(
                    start_key=form_entity_id,
                    end_key=field_id,
                    rel_type="HAS_FIELD",
                    field_name=field.get("field_name", ""),
                    required=field.get("required", False)
                )
                relationships_created += 1
                logger.debug(
                    f"Created relationship: {form_entity_id} -[HAS_FIELD]-> {field_id}"
                )
        else:
            logger.warning(
                f"Form field '{field_id}' references non-existent form_id: '{field_form_id}'"
            )
    
    logger.info(f"Created {relationships_created} form-field relationships")
    return relationships_created


def create_parent_module_relationships(
    json_file_path: str | Path,
    graph: GraphData
) -> int:
    """
    Create BELONGS_TO relationships between entities and their parent modules.
    
    Args:
        json_file_path: Path to the JSON file containing entities
        graph: GraphData object to add relationships to
        
    Returns:
        Number of relationships created
    """
    json_path = Path(json_file_path)
    
    if not json_path.exists():
        logger.error(f"JSON file not found: {json_path}")
        return 0
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            entities = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON file {json_path}: {e}")
        return 0
    
    if not isinstance(entities, list):
        logger.error(f"Expected a list of entities, got {type(entities)}")
        return 0
    
    relationships_created = 0
    
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        
        entity_id = entity.get("id")
        parent_module = entity.get("parent_module")
        
        if entity_id and parent_module:
            # Create relationship: Entity -[BELONGS_TO]-> Module
            graph.add_relationship(
                start_key=entity_id,
                end_key=parent_module,
                rel_type="BELONGS_TO",
                entity_type=entity.get("type", "")
            )
            relationships_created += 1
            logger.debug(
                f"Created relationship: {entity_id} -[BELONGS_TO]-> {parent_module}"
            )
    
    logger.info(f"Created {relationships_created} parent-module relationships")
    return relationships_created


def compose_manual_tasks(
    json_file_path: str | Path,
    graph: GraphData
) -> Dict[str, int]:
    """
    Compose and execute all manual relationship creation tasks.
    
    This function serves as the main entry point for manual relationship creation.
    It calls all individual task functions and aggregates their results.
    
    Args:
        json_file_path: Path to the JSON file containing entities
        graph: GraphData object to add relationships to
        
    Returns:
        Dictionary mapping task names to the number of relationships created
        
    Example:
        >>> from core import GraphData
        >>> graph = GraphData()
        >>> results = compose_manual_tasks("entities.json", graph)
        >>> print(f"Total relationships: {sum(results.values())}")
    """
    json_path = Path(json_file_path)
    
    logger.info(f"Starting manual relationship creation for: {json_path}")
    
    results = {}
    
    # Task 1: Create form-field relationships
    logger.info("Task 1: Creating form-field relationships...")
    results["form_field_relationships"] = create_form_field_relationships(json_path, graph)
    
    # # Task 2: Create parent-module relationships
    # logger.info("Task 2: Creating parent-module relationships...")
    # results["parent_module_relationships"] = create_parent_module_relationships(json_path, graph)
    
    # Future tasks can be added here
    # Task 3: Create screen-component relationships
    # results["screen_component_relationships"] = create_screen_component_relationships(json_path, graph)
    
    total = sum(results.values())
    logger.info(f"Manual relationship creation complete. Total: {total} relationships")
    
    return results


def apply_manual_tasks_to_pipeline(
    json_file_path: str | Path,
    graph: GraphData,
    task_names: List[str] | None = None
) -> Dict[str, int]:
    """
    Apply specific manual tasks to the graph pipeline.
    
    This function allows selective execution of manual tasks.
    
    Args:
        json_file_path: Path to the JSON file containing entities
        graph: GraphData object to add relationships to
        task_names: List of task names to execute. If None, all tasks are executed.
                   Available tasks: ["form_field", "parent_module"]
        
    Returns:
        Dictionary mapping task names to the number of relationships created
    """
    json_path = Path(json_file_path)
    
    available_tasks = {
        "form_field": create_form_field_relationships,
        # "parent_module": create_parent_module_relationships,
    }
    
    if task_names is None:
        task_names = list(available_tasks.keys())
    
    results = {}
    
    for task_name in task_names:
        if task_name not in available_tasks:
            logger.warning(f"Unknown task: {task_name}. Skipping.")
            continue
        
        logger.info(f"Executing task: {task_name}")
        task_func = available_tasks[task_name]
        count = task_func(json_path, graph)
        results[task_name] = count
    
    return results
