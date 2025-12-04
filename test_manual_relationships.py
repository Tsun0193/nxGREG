"""
Quick test script to verify manual relationship creation works correctly.
"""

from pathlib import Path
from core import GraphData
from ingest.manual_creation import compose_manual_tasks


def test_manual_relationships():
    """Test the manual relationship creation on contract-list-entities.json."""
    print("Testing manual relationship creation...\n")
    
    # Get the JSON file path
    json_file = Path(__file__).parent / "json" / "contract-list-entities.json"
    
    if not json_file.exists():
        print(f"ERROR: JSON file not found: {json_file}")
        return False
    
    print(f"Reading from: {json_file}\n")
    
    # Create graph
    graph = GraphData()
    
    # Run manual relationship creation
    try:
        results = compose_manual_tasks(json_file, graph)
        
        print("\n" + "="*60)
        print("RESULTS:")
        print("="*60)
        for task_name, count in results.items():
            print(f"  {task_name}: {count} relationships")
        
        total_relationships = sum(results.values())
        print(f"\nTotal relationships created: {total_relationships}")
        print(f"Total nodes in graph: {len(graph.nodes)}")
        print(f"Total edges in graph: {len(graph.relationships)}")
        
        # Show some sample relationships
        if graph.relationships:
            print("\n" + "="*60)
            print("SAMPLE RELATIONSHIPS (first 10):")
            print("="*60)
            for i, rel in enumerate(graph.relationships[:10], 1):
                print(f"{i}. {rel.start_key} -[{rel.rel_type}]-> {rel.end_key}")
        
        print("\n✓ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    success = test_manual_relationships()
    exit(0 if success else 1)
