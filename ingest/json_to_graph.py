"""Pipeline to read JSON entities and relationships and load them into Neo4j graph database."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Any

from core import GraphData
from loading.loader import Neo4jLoader
from ingest.entity_deduplicator import EntityDeduplicator
from ingest.manual_creation import compose_manual_tasks

from dotenv import load_dotenv

load_dotenv()


class JSONToGraphPipeline:
    """Reads entity and relationship JSON files and loads them into a graph database."""

    def __init__(
        self,
        json_dir: str | Path,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        use_deduplicator: bool = False,
    ):
        """
        Initialize the pipeline.

        Args:
            json_dir: Directory containing JSON files with entities and relationships
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            use_deduplicator: If True, use EntityDeduplicator to merge duplicate entities
        """
        self.json_dir = Path(json_dir)
        self.loader = Neo4jLoader(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)
        self.graph = GraphData()
        self.use_deduplicator = use_deduplicator
        self.deduplicator = EntityDeduplicator() if use_deduplicator else None

    @staticmethod
    def _sanitize_properties(properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Final sanitization to ensure all property values are Neo4j-compatible primitives.

        Args:
            properties: Dictionary to sanitize

        Returns:
            Dictionary with only primitive values or arrays of primitives
        """
        sanitized = {}

        for key, value in properties.items():
            if value is None:
                sanitized[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list):
                # Ensure all list items are primitives
                if all(isinstance(item, (str, int, float, bool, type(None))) for item in value):
                    sanitized[key] = [str(item) if item is None else item for item in value]
                else:
                    # If list contains complex types, convert to JSON string
                    sanitized[key] = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, dict):
                # Convert nested dict to JSON string if present
                sanitized[key] = json.dumps(value, ensure_ascii=False)
            else:
                # Convert any other type to string
                sanitized[key] = str(value)

        return sanitized

    def _add_entity_to_graph(
        self,
        entity_id: str,
        entity_type: str,
        properties: Dict[str, Any],
    ) -> None:
        """
        Add an entity to the graph, using deduplicator if enabled.

        Args:
            entity_id: Unique entity ID
            entity_type: Type of entity
            properties: Entity properties
        """
        properties["uid"] = entity_id
        properties = self._sanitize_properties(properties)

        labels = [entity_type]
        self.graph.add_node(key=entity_id, labels=labels, **properties)

    @staticmethod
    def _flatten_properties(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """
        Flatten nested dictionaries using underscore notation.
        Convert lists and remaining complex types to JSON strings.
        
        NOTE: This method is not needed for v5 format JSON files which are already flattened.
        It's kept for backward compatibility with older JSON formats.
        
        Args:
            data: Dictionary to flatten
            prefix: Prefix for nested keys
            
        Returns:
            Flattened dictionary with only primitive types (str, int, float, bool)
        """
        flattened = {}
        
        for key, value in data.items():
            # Use underscore instead of dot to avoid Neo4j interpreting as nested
            new_key = f"{prefix}_{key}" if prefix else key
            
            if value is None:
                flattened[new_key] = ""
            elif isinstance(value, bool):
                # Handle boolean explicitly before checking int (bool is subclass of int)
                flattened[new_key] = value
            elif isinstance(value, (int, float)):
                flattened[new_key] = value
            elif isinstance(value, str):
                flattened[new_key] = value
            elif isinstance(value, dict):
                # Recursively flatten nested dicts
                nested = JSONToGraphPipeline._flatten_properties(value, new_key)
                flattened.update(nested)
            elif isinstance(value, list):
                # Check if list contains only primitives
                if all(isinstance(item, (str, int, float, bool, type(None))) for item in value):
                    # Store as Neo4j array (convert None to empty string)
                    flattened[new_key] = [str(item) if item is None else item for item in value]
                else:
                    # Complex list - convert to JSON string
                    flattened[new_key] = json.dumps(value, ensure_ascii=False)
            else:
                # Convert any other type to string
                flattened[new_key] = str(value)
        
        return flattened

    def load_entities_from_file(self, file_path: Path) -> None:
        """
        Load entities from a JSON file into the graph.

        Expected JSON structure (list of entities):
        [
            {
                "id": "unique_id",
                "type": "entity_type",
                "name": "Entity Name",
                "properties": {...},
                ...
            }
        ]
        """
        print(f"Loading entities from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            entities = json.load(f)

        if not isinstance(entities, list):
            print(f"Warning: {file_path} does not contain a list of entities. Skipping.")
            return

        for entity in entities:
            if not isinstance(entity, dict):
                continue

            entity_id = entity.get("id")
            entity_type = entity.get("type")

            if not entity_id or not entity_type:
                print(f"Warning: Entity missing 'id' or 'type': {entity}")
                continue

            # Extract properties (already flattened in v5 format)
            properties = {k: v for k, v in entity.items() if k not in ["id", "type"]}
            properties["uid"] = entity_id
            
            # Sanitize to ensure Neo4j compatibility
            properties = self._sanitize_properties(properties)

            # Create node with entity type as label
            labels = [entity_type]
            self.graph.add_node(key=entity_id, labels=labels, **properties)

        print(f"Loaded {len(entities)} entities from {file_path.name}")

    def load_relationships_from_file(self, file_path: Path) -> None:
        """
        Load relationships from a JSON file into the graph.

        Expected JSON structure:
        {
            "relationships": [
                {
                    "source": "source_id",
                    "target": "target_id",
                    "relationship_type": "REL_TYPE",
                    "properties": {...}
                }
            ]
        }
        """
        print(f"Loading relationships from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        relationships = data.get("relationships", [])
        if not relationships:
            print(f"Warning: No relationships found in {file_path}")
            return

        for rel in relationships:
            if not isinstance(rel, dict):
                continue

            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("relationship_type")

            if not source or not target or not rel_type:
                print(f"Warning: Relationship missing required fields: {rel}")
                continue

            # Extract relationship properties (already flattened in v5 format)
            properties = rel.get("properties", {})
            
            # Sanitize to ensure Neo4j compatibility
            properties = self._sanitize_properties(properties)

            self.graph.add_relationship(
                start_key=source,
                end_key=target,
                rel_type=rel_type,
                **properties,
            )

        print(f"Loaded {len(relationships)} relationships from {file_path.name}")

    def load_from_mixed_file(self, file_path: Path) -> None:
        """
        Load both entities and relationships from a single JSON file.

        Supports multiple formats:
        1. List of entities (detected by having 'id' and 'type' fields)
        2. Object with 'relationships' key
        3. Object with both 'entities' and 'relationships' keys
        """
        print(f"Loading from mixed file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        entity_count = 0
        relationship_count = 0

        # Case 1: Data is a list (assume entities)
        if isinstance(data, list):
            # Check if it's a list of entities
            if data and isinstance(data[0], dict) and "id" in data[0] and "type" in data[0]:
                for entity in data:
                    if not isinstance(entity, dict):
                        continue

                    entity_id = entity.get("id")
                    entity_type = entity.get("type")

                    if not entity_id or not entity_type:
                        continue

                    # Extract properties (already flattened in v5 format)
                    properties = {k: v for k, v in entity.items() if k not in ["id", "type"]}

                    if self.use_deduplicator:
                        # Add to deduplicator for merging
                        self.deduplicator.add_entity(entity, file_path.name)
                    else:
                        # Add directly to graph
                        self._add_entity_to_graph(entity_id, entity_type, properties)
                        entity_count += 1

        # Case 2: Data is a dict
        elif isinstance(data, dict):
            # Load entities if present
            entities = data.get("entities", [])
            if entities:
                for entity in entities:
                    if not isinstance(entity, dict):
                        continue

                    entity_id = entity.get("id")
                    entity_type = entity.get("type")

                    if not entity_id or not entity_type:
                        continue

                    # Extract properties (already flattened in v5 format)
                    properties = {k: v for k, v in entity.items() if k not in ["id", "type"]}

                    if self.use_deduplicator:
                        # Add to deduplicator for merging
                        self.deduplicator.add_entity(entity, file_path.name)
                    else:
                        # Add directly to graph
                        self._add_entity_to_graph(entity_id, entity_type, properties)
                        entity_count += 1

            # Load relationships if present
            relationships = data.get("relationships", [])
            if relationships:
                for rel in relationships:
                    if not isinstance(rel, dict):
                        continue

                    source = rel.get("source")
                    target = rel.get("target")
                    rel_type = rel.get("relationship_type")

                    if not source or not target or not rel_type:
                        continue

                    # Extract relationship properties (already flattened in v5 format)
                    properties = rel.get("properties", {})

                    # Sanitize to ensure Neo4j compatibility
                    properties = self._sanitize_properties(properties)

                    self.graph.add_relationship(
                        start_key=source,
                        end_key=target,
                        rel_type=rel_type,
                        **properties,
                    )
                    relationship_count += 1

        print(f"  → Loaded {entity_count} entities and {relationship_count} relationships from {file_path.name}")

    def apply_manual_relationships(
        self,
        json_files: List[Path] = None,
    ) -> Dict[str, int]:
        """
        Apply manual relationship creation tasks to the graph.
        
        Args:
            json_files: List of JSON files to process. If None, processes all JSON files in json_dir.
            
        Returns:
            Dictionary mapping task names to relationship counts
        """
        print("\n=== Applying Manual Relationships ===")
        
        if json_files is None:
            json_files = sorted(self.json_dir.glob("*.json"))
        
        total_results = {}
        
        for json_file in json_files:
            print(f"Processing manual relationships for: {json_file.name}")
            results = compose_manual_tasks(json_file, self.graph)
            
            # Aggregate results
            for task_name, count in results.items():
                total_results[task_name] = total_results.get(task_name, 0) + count
        
        print(f"\n=== Manual Relationships Summary ===")
        for task_name, count in total_results.items():
            print(f"  {task_name}: {count}")
        
        total_count = sum(total_results.values())
        print(f"Total manual relationships created: {total_count}")
        
        return total_results

    def load_all_json_files(
        self,
        entity_patterns: List[str] = None,
        relationship_patterns: List[str] = None,
        use_mixed_mode: bool = True,
    ) -> None:
        """
        Load all JSON files from the json directory.

        Args:
            entity_patterns: List of filename patterns for entity files (e.g., ["entities", "component"])
            relationship_patterns: List of filename patterns for relationship files (e.g., ["relationships"])
            use_mixed_mode: If True, use load_from_mixed_file for all files (recommended)
        """
        if use_mixed_mode:
            # New approach: Load all JSON files and auto-detect content
            print("\n=== Loading All JSON Files (Mixed Mode) ===")
            for json_file in sorted(self.json_dir.glob("*.json")):
                self.load_from_mixed_file(json_file)

            # If using deduplicator, finalize and add deduplicated entities to graph
            if self.use_deduplicator:
                self._finalize_deduplication()
        else:
            # Legacy approach: Separate entity and relationship files
            if entity_patterns is None:
                entity_patterns = ["entities", "component"]

            if relationship_patterns is None:
                relationship_patterns = ["relationships", "relationship"]

            # Load entity files
            print("\n=== Loading Entity Files ===")
            for json_file in sorted(self.json_dir.glob("*.json")):
                if any(pattern in json_file.stem.lower() for pattern in entity_patterns):
                    self.load_entities_from_file(json_file)

            # Load relationship files
            print("\n=== Loading Relationship Files ===")
            for json_file in sorted(self.json_dir.glob("*.json")):
                if any(pattern in json_file.stem.lower() for pattern in relationship_patterns):
                    self.load_relationships_from_file(json_file)

    def load_to_neo4j(self, wipe: bool = False) -> None:
        """
        Load the graph data into Neo4j.

        Args:
            wipe: If True, delete all existing data in Neo4j before loading
        """
        print(f"\n=== Loading to Neo4j ===")
        print(f"Total nodes: {len(self.graph.nodes)}")
        print(f"Total relationships: {len(self.graph.relationships)}")

        self.loader.load(self.graph, wipe=wipe)
        print("Successfully loaded data into Neo4j!")

    def _finalize_deduplication(self) -> None:
        """
        Finalize deduplication and add all deduplicated entities to the graph.
        """
        print("\n=== Finalizing Deduplication ===")

        # Get merge report
        report = self.deduplicator.get_merge_report()
        print(f"Total Entities: {report['total_entities']}")
        print(f"Merged Entities: {report['merged_entities']}")
        print(f"New Entities: {report['new_entities']}")
        print(f"Merge Operations: {report['merge_operations']}")

        # Add all deduplicated entities to graph
        for entity in self.deduplicator.get_all_entities():
            entity_id = entity.get("id")
            entity_type = entity.get("type")

            if not entity_id or not entity_type:
                continue

            # Extract properties (remove internal tracking fields)
            properties = {
                k: v for k, v in entity.items()
                if k not in ["id", "type"] and not k.startswith("_")
            }

            self._add_entity_to_graph(entity_id, entity_type, properties)

        print(f"Added {report['total_entities']} deduplicated entities to graph")

    def run(
        self,
        entity_patterns: List[str] = None,
        relationship_patterns: List[str] = None,
        wipe: bool = False,
        use_mixed_mode: bool = True,
        apply_manual_relationships: bool = True,
    ) -> None:
        """
        Run the complete pipeline: load JSON files and ingest into Neo4j.

        Args:
            entity_patterns: List of filename patterns for entity files (ignored if use_mixed_mode=True)
            relationship_patterns: List of filename patterns for relationship files (ignored if use_mixed_mode=True)
            wipe: If True, delete all existing data in Neo4j before loading
            use_mixed_mode: If True, auto-detect entities and relationships in all JSON files
            apply_manual_relationships: If True, apply manual relationship creation after loading entities
        """
        self.load_all_json_files(
            entity_patterns=entity_patterns,
            relationship_patterns=relationship_patterns,
            use_mixed_mode=use_mixed_mode,
        )
        
        # Apply manual relationship creation if enabled
        if apply_manual_relationships:
            self.apply_manual_relationships()
        
        self.load_to_neo4j(wipe=wipe)

    def close(self) -> None:
        """Close the Neo4j connection."""
        self.loader.close()


def main():
    """Main entry point for the pipeline."""
    # Get configuration from environment variables
    neo4j_uri = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

    # Get the project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    json_dir = project_root / "json"
    
    print("done")

    # Create and run the pipeline
    pipeline = JSONToGraphPipeline(
        json_dir=json_dir,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
    )

    try:
        print(f"Starting JSON to Graph pipeline...")
        print(f"JSON directory: {json_dir}")
        print(f"Neo4j URI: {neo4j_uri}")

        # Run the pipeline with default patterns
        # Set wipe=True to clear existing data, or False to append
        # apply_manual_relationships=True to enable manual relationship creation
        pipeline.run(wipe=True, apply_manual_relationships=True)

    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
