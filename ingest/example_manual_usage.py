"""
Example usage of the manual relationship creation module.

This script demonstrates how to use the manual_creation functions
to create relationships between entities in a JSON file.
"""

from pathlib import Path
from core import GraphData
from ingest.manual_creation import (
    create_form_field_relationships,
    create_parent_module_relationships,
    compose_manual_tasks,
    apply_manual_tasks_to_pipeline,
)


def example_basic_usage():
    """Example: Basic usage with compose_manual_tasks."""
    print("=== Example 1: Basic Usage ===\n")
    
    # Path to your JSON file
    json_file = Path(__file__).parent.parent / "json" / "contract-list-entities.json"
    
    # Create a GraphData object
    graph = GraphData()
    
    # Run all manual tasks
    results = compose_manual_tasks(json_file, graph)
    
    # Print results
    print(f"\nResults:")
    for task_name, count in results.items():
        print(f"  {task_name}: {count} relationships created")
    
    print(f"\nTotal nodes in graph: {len(graph.nodes)}")
    print(f"Total relationships in graph: {len(graph.relationships)}")


def example_selective_tasks():
    """Example: Run only specific tasks."""
    print("\n=== Example 2: Selective Task Execution ===\n")
    
    json_file = Path(__file__).parent.parent / "json" / "contract-list-entities.json"
    graph = GraphData()
    
    # Run only the form_field relationship creation task
    results = apply_manual_tasks_to_pipeline(
        json_file,
        graph,
        task_names=["form_field"]  # Only run this task
    )
    
    print(f"\nResults:")
    for task_name, count in results.items():
        print(f"  {task_name}: {count} relationships created")


def example_individual_functions():
    """Example: Call individual relationship creation functions."""
    print("\n=== Example 3: Individual Function Calls ===\n")
    
    json_file = Path(__file__).parent.parent / "json" / "contract-list-entities.json"
    graph = GraphData()
    
    # Create form-field relationships
    print("Creating form-field relationships...")
    form_field_count = create_form_field_relationships(json_file, graph)
    print(f"Created {form_field_count} form-field relationships")
    
    # Create parent-module relationships
    print("\nCreating parent-module relationships...")
    parent_module_count = create_parent_module_relationships(json_file, graph)
    print(f"Created {parent_module_count} parent-module relationships")
    
    print(f"\nTotal relationships: {form_field_count + parent_module_count}")


def example_inspection():
    """Example: Inspect created relationships."""
    print("\n=== Example 4: Inspect Created Relationships ===\n")
    
    json_file = Path(__file__).parent.parent / "json" / "contract-list-entities.json"
    graph = GraphData()
    
    # Create relationships
    compose_manual_tasks(json_file, graph)
    
    # Inspect relationships
    print("\nSample relationships created:")
    for i, rel in enumerate(graph.relationships[:5]):  # Show first 5
        print(f"{i+1}. {rel.start_key} -[{rel.rel_type}]-> {rel.end_key}")
        if rel.properties:
            print(f"   Properties: {rel.properties}")
    
    if len(graph.relationships) > 5:
        print(f"... and {len(graph.relationships) - 5} more relationships")


def main():
    """Run all examples."""
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    
    try:
        example_basic_usage()
        # example_selective_tasks()
        # example_individual_functions()
        # example_inspection()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
