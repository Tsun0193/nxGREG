"""Example script demonstrating how to use the JSON to Graph pipeline."""

import os
from pathlib import Path
from ingest import JSONToGraphPipeline


def main():
    """Example usage of the JSONToGraphPipeline."""
    
    # Configuration - update these with your Neo4j credentials
    neo4j_uri = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    
    # Path to JSON directory
    json_dir = Path("json/simple")
    
    # Create the pipeline
    pipeline = JSONToGraphPipeline(
        json_dir=json_dir,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
    )
    
    try:
        # # Option 1: Run with mixed mode (RECOMMENDED - auto-detects entities and relationships)
        # print("Running complete pipeline with mixed mode...")
        # pipeline.run(wipe=True, use_mixed_mode=True)
        
        # # Option 2: Run with legacy mode (separate entity and relationship patterns)
        # # pipeline.run(
        # #     entity_patterns=["entities", "component"],
        # #     relationship_patterns=["relationships"],
        # #     wipe=True,
        # #     use_mixed_mode=False
        # # )
        
        # # Option 3: Load specific files manually
        # # Mixed file (contains both entities and relationships)
        # pipeline.load_from_mixed_file(json_dir / "contract-list-component-entities_v3.json")
        
        # Separate files
        print(json_dir)
        # Use load_from_mixed_file for v3 format (has both entities and relationships keys)
        # pipeline.load_from_mixed_file(json_dir / "contract-list-entities.json")
        # pipeline.load_from_mixed_file(json_dir / "contract-list-ui-interaction-entities.json")
        # pipeline.load_from_mixed_file(json_dir / "contract-list-component-entities.json")     
        # pipeline.load_from_mixed_file(json_dir / "contract-list-database-entities.json")
        # pipeline.load_from_mixed_file(json_dir / "contract-list-database-relationships.json")
        # pipeline.load_from_mixed_file(json_dir / "contract-list-cross-layer-relationships.json")

        # pipeline.load_relationships_from_file(json_dir / "contract-list-cross-layer-relationships.json")
        
        # pipeline.run(wipe=True, apply_manual_relationships=True)
        
        files = os.listdir(json_dir)
        print(files)
        for f in files:
            # file_path = json_dir / f
            # print(file_path)
            pipeline.load_from_mixed_file(json_dir / f)

            
        
        # Then load to Neo4j
        pipeline.load_to_neo4j(wipe=True)
        
        print("\n✓ Pipeline completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
