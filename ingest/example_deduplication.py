"""Example script demonstrating entity deduplication before loading to Neo4j."""

import os
from pathlib import Path
from dotenv import load_dotenv

from ingest.entity_deduplicator import EntityDeduplicator
from ingest.json_to_graph import JSONToGraphPipeline

load_dotenv()


def example_1_deduplicator_only():
    """
    Example 1: Using EntityDeduplicator standalone to merge entities from multiple files.

    This approach:
    - Loads entities from multiple JSON files
    - Automatically detects duplicates (by ID or table_name)
    - Merges properties intelligently
    - Exports deduplicated entities to a new JSON file
    """
    print("=" * 70)
    print("EXAMPLE 1: Deduplicator Only (No Neo4j)")
    print("=" * 70)

    # Initialize deduplicator
    dedup = EntityDeduplicator()

    # Path to JSON directory
    json_dir = Path(__file__).parent.parent / "json"

    # Load entities from multiple files with priority order
    # Files matching earlier patterns are loaded first
    files = list(json_dir.glob("contract-list-*.json"))

    print(f"\nLoading {len(files)} JSON files...")
    dedup.load_from_multiple_files(
        files,
        priority_order=[
            "database-entities-v2",  # Load this first (baseline)
            "component-entities",  # Then load component entities (may contain updates)
        ],
    )

    # Get merge report
    print("\n" + "=" * 70)
    report = dedup.get_merge_report()
    print(f"\nMerge Report:")
    print(f"  Total Entities: {report['total_entities']}")
    print(f"  Merged Entities: {report['merged_entities']}")
    print(f"  New Entities: {report['new_entities']}")
    print(f"  Merge Operations: {report['merge_operations']}")

    # Export deduplicated entities
    output_dir = json_dir / "deduplicated"
    output_dir.mkdir(exist_ok=True)

    dedup.export_deduplicated_entities(output_dir / "entities_deduplicated.json")
    dedup.export_merge_report(output_dir / "merge_report.json")

    # Print sample of merged entities
    print("\n" + "=" * 70)
    print("Sample of Merged Database Tables:")
    print("=" * 70)

    db_tables = [e for e in dedup.get_all_entities() if e.get("type") == "database_table"]
    for table in db_tables[:5]:  # Show first 5
        print(f"\n  ID: {table.get('id')}")
        print(f"  Name: {table.get('name')}")
        print(f"  Table Name: {table.get('table_name')}")
        print(f"  Source Files: {table.get('_source_files', [])}")


def example_2_with_neo4j():
    """
    Example 2: Using deduplicator integrated with JSONToGraphPipeline.

    This approach:
    - Creates a pipeline with deduplicator enabled
    - Loads all JSON files with automatic deduplication
    - Merges duplicate entities
    - Loads the deduplicated graph into Neo4j
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: With Neo4j Integration")
    print("=" * 70)

    # Get Neo4j configuration
    neo4j_uri = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

    # Get paths
    json_dir = Path(__file__).parent.parent / "json"

    print(f"\nNeo4j URI: {neo4j_uri}")
    print(f"JSON Directory: {json_dir}")

    # Create pipeline WITH deduplicator enabled
    pipeline = JSONToGraphPipeline(
        json_dir=json_dir,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        use_deduplicator=True,  # Enable deduplication!
    )

    try:
        print("\nStarting pipeline with deduplication...")
        # Note: Set wipe=True to clear existing data, wipe=False to append
        pipeline.run(wipe=True)

        # Print merge report from pipeline's deduplicator
        if pipeline.deduplicator:
            report = pipeline.deduplicator.get_merge_report()
            print("\n" + "=" * 70)
            print("Final Deduplication Report:")
            print("=" * 70)
            print(f"Total Entities: {report['total_entities']}")
            print(f"Merged Entities: {report['merged_entities']}")
            print(f"New Entities: {report['new_entities']}")

    finally:
        pipeline.close()


def example_3_manual_deduplication():
    """
    Example 3: Manual deduplication - detect and display potential duplicates.

    This approach:
    - Shows how to find duplicate entities by various criteria
    - Helpful for reviewing what would be merged
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Manual Duplicate Detection")
    print("=" * 70)

    dedup = EntityDeduplicator()
    json_dir = Path(__file__).parent.parent / "json"

    # Load files
    files = list(json_dir.glob("contract-list-*.json"))
    dedup.load_from_multiple_files(files)

    # Find duplicates by entity type
    print("\n" + "=" * 70)
    print("Checking for duplicate database_table entities by name...")
    print("=" * 70)

    db_table_duplicates = dedup.find_duplicates_by_type("database_table")

    if db_table_duplicates:
        print(f"\nFound {len(db_table_duplicates)} potential duplicate groups:\n")
        for name, entity_ids in db_table_duplicates[:5]:  # Show first 5
            print(f"  {name}:")
            for eid in entity_ids:
                entity = dedup.get_entity_by_id(eid)
                print(f"    - {eid}")
                print(f"      Properties: {list(entity.keys())}")
    else:
        print("\nNo duplicates found by name.")

    # Print statistics
    print("\n" + "=" * 70)
    print("Entity Type Statistics:")
    print("=" * 70)

    type_counts = {}
    for entity in dedup.get_all_entities():
        etype = entity.get("type")
        type_counts[etype] = type_counts.get(etype, 0) + 1

    for etype, count in sorted(type_counts.items()):
        print(f"  {etype}: {count}")


if __name__ == "__main__":
    # Run examples
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == "1":
            example_1_deduplicator_only()
        elif example_num == "2":
            example_2_with_neo4j()
        elif example_num == "3":
            example_3_manual_deduplication()
        else:
            print(f"Unknown example: {example_num}")
            print("Usage: python example_deduplication.py [1|2|3]")
    else:
        # Run example 1 by default (no Neo4j needed)
        example_1_deduplicator_only()
        print("\n" + "=" * 70)
        print("To run other examples:")
        print("  python example_deduplication.py 2   # Load to Neo4j with deduplication")
        print("  python example_deduplication.py 3   # Manual duplicate detection")
        print("=" * 70)
