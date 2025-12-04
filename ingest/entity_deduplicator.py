"""Module for deduplicating and merging entities from multiple JSON sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict


class EntityDeduplicator:
    """Handles deduplication and merging of entities from multiple JSON files."""

    def __init__(self):
        """Initialize the deduplicator."""
        self.entities_by_id: Dict[str, Dict[str, Any]] = {}
        self.entities_by_table_name: Dict[str, List[str]] = defaultdict(list)  # For database_table entities
        self.entities_by_name: Dict[str, List[str]] = defaultdict(list)  # Generic name-based lookup
        self.merge_history: List[Dict[str, Any]] = []

    def add_entity(
        self, entity: Dict[str, Any], source_file: str = "unknown"
    ) -> Tuple[str, bool]:
        """
        Add an entity to the deduplicator.

        Args:
            entity: Entity dictionary with 'id', 'type', and other properties
            source_file: Source file for tracking purposes

        Returns:
            Tuple of (entity_id, is_new) where is_new indicates if it's a new entity or a merge
        """
        entity_id = entity.get("id")
        entity_type = entity.get("type")
        
        if not entity_id or not entity_type:
            raise ValueError(f"Entity missing 'id' or 'type': {entity}")
        
        # Check if entity already exists by exact ID
        if entity_id in self.entities_by_id:
            # Merge properties with existing entity
            self._merge_entity(entity_id, entity, source_file)
            return entity_id, False
        
        # For database_table type, check for duplicates by table_name
        if entity_type == "database_table":
            table_name = entity.get("table_name")
            if table_name:
                # Check if this table already exists under a different ID
                duplicate_id = self._find_duplicate_by_table_name(table_name, entity_id)
                if duplicate_id:
                    # Merge into existing entity
                    self._merge_entity(duplicate_id, entity, source_file)
                    return duplicate_id, False
                
                # Track this table name
                self.entities_by_table_name[table_name].append(entity_id)
        
        # New entity - add it
        self.entities_by_id[entity_id] = entity.copy()
        self.entities_by_id[entity_id]["_source_files"] = [source_file]
        self.entities_by_id[entity_id]["_is_merged"] = False
        
        # Track by name for general lookup
        name = entity.get("name")
        if name:
            self.entities_by_name[name].append(entity_id)
        
        return entity_id, True

    def _find_duplicate_by_table_name(self, table_name: str, current_id: str) -> str | None:
        """
        Find if a table with the same table_name already exists.
        
        Args:
            table_name: The table name to search for
            current_id: The current entity ID (to exclude from search)
            
        Returns:
            The ID of the duplicate entity if found, None otherwise
        """
        if table_name in self.entities_by_table_name:
            existing_ids = self.entities_by_table_name[table_name]
            # Return the first existing ID (they should all point to the same logical table)
            if existing_ids:
                return existing_ids[0]
        return None

    def _merge_entity(
        self, 
        existing_id: str, 
        new_entity: Dict[str, Any], 
        source_file: str
    ) -> None:
        """
        Merge new entity properties into existing entity.
        
        Strategy:
        1. Keep existing ID
        2. For each property in new_entity:
           - If property is missing in existing: add it
           - If property exists and values differ: keep existing but log the difference
           - If property exists and values are the same: no change
        3. Merge special fields like source_files and parent_module
        
        Args:
            existing_id: ID of the existing entity to merge into
            new_entity: New entity with properties to merge
            source_file: Source file of the new entity
        """
        existing = self.entities_by_id[existing_id]
        
        # Track merge history
        merge_record = {
            "target_id": existing_id,
            "source_file": source_file,
            "properties_added": [],
            "properties_updated": [],
            "properties_skipped": [],
        }
        
        for key, new_value in new_entity.items():
            if key in ["id", "_source_files", "_is_merged"]:
                continue
            
            if key not in existing:
                # New property - add it
                existing[key] = new_value
                merge_record["properties_added"].append(key)
            else:
                existing_value = existing[key]
                
                # Compare values
                if existing_value != new_value:
                    # Values differ - decide which to keep
                    # Strategy: keep existing value for core properties, but update if existing is empty/None
                    if not existing_value and new_value:
                        existing[key] = new_value
                        merge_record["properties_updated"].append(f"{key}: {existing_value} → {new_value}")
                    else:
                        merge_record["properties_skipped"].append(
                            f"{key}: existing={existing_value}, new={new_value}"
                        )
                # If values are the same, do nothing
        
        # Update source files tracking
        if "_source_files" not in existing:
            existing["_source_files"] = []
        if source_file not in existing["_source_files"]:
            existing["_source_files"].append(source_file)
        
        existing["_is_merged"] = True
        self.merge_history.append(merge_record)

    def load_from_file(self, file_path: Path, source_label: str = None) -> int:
        """
        Load entities from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            source_label: Optional label for the source (defaults to filename)
            
        Returns:
            Number of entities loaded
        """
        source_label = source_label or file_path.name
        
        print(f"Loading entities from: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Extract entities based on JSON structure
        entities = []
        if isinstance(data, dict):
            if "entities" in data:
                entities = data["entities"]
            elif "id" in data and "type" in data:
                # Single entity
                entities = [data]
        elif isinstance(data, list):
            entities = data
        
        entity_count = 0
        for entity in entities:
            if not isinstance(entity, dict):
                continue
            try:
                entity_id, is_new = self.add_entity(entity, source_label)
                if is_new:
                    entity_count += 1
            except ValueError as e:
                print(f"  Warning: {e}")
        
        print(f"  → {entity_count} new entities, {len(entities) - entity_count} merged")
        return entity_count

    def load_from_multiple_files(
        self, 
        file_paths: List[Path],
        priority_order: List[str] = None
    ) -> Dict[str, int]:
        """
        Load entities from multiple files, with optional priority ordering.
        
        Args:
            file_paths: List of paths to JSON files
            priority_order: Optional list of file patterns in priority order
                          Files matching earlier patterns are loaded first
                          
        Returns:
            Dictionary with stats: {filename: count_added}
        """
        # Sort files by priority if specified
        if priority_order:
            def get_priority(path: Path) -> int:
                filename = path.name.lower()
                for i, pattern in enumerate(priority_order):
                    if pattern.lower() in filename:
                        return i
                return len(priority_order)
            
            sorted_paths = sorted(file_paths, key=get_priority)
        else:
            sorted_paths = sorted(file_paths)
        
        stats = {}
        total_new = 0
        total_merged = 0
        
        print("\n=== Loading Entities from Multiple Files ===")
        for file_path in sorted_paths:
            before_count = len(self.entities_by_id)
            self.load_from_file(file_path)
            after_count = len(self.entities_by_id)
            new_count = after_count - before_count
            stats[file_path.name] = new_count
            total_new += new_count
        
        return stats

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """
        Get all deduplicated entities as a list.
        
        Returns:
            List of entity dictionaries
        """
        return list(self.entities_by_id.values())

    def get_entity_by_id(self, entity_id: str) -> Dict[str, Any] | None:
        """Get a specific entity by ID."""
        return self.entities_by_id.get(entity_id)

    def find_duplicates_by_type(self, entity_type: str) -> List[Tuple[str, List[str]]]:
        """
        Find potential duplicate entities by type and similarity.
        
        Args:
            entity_type: Type of entities to check
            
        Returns:
            List of (field, [entity_ids]) tuples for entities with same field value
        """
        type_entities = {
            eid: entity for eid, entity in self.entities_by_id.items()
            if entity.get("type") == entity_type
        }
        
        # Group by name
        by_name = defaultdict(list)
        for eid, entity in type_entities.items():
            name = entity.get("name", "")
            if name:
                by_name[name].append(eid)
        
        # Return only those with duplicates
        return [(name, ids) for name, ids in by_name.items() if len(ids) > 1]

    def get_merge_report(self) -> Dict[str, Any]:
        """
        Get a report of all merge operations performed.
        
        Returns:
            Dictionary with merge statistics and history
        """
        merged_count = sum(1 for e in self.entities_by_id.values() if e.get("_is_merged", False))
        
        return {
            "total_entities": len(self.entities_by_id),
            "merged_entities": merged_count,
            "new_entities": len(self.entities_by_id) - merged_count,
            "merge_operations": len(self.merge_history),
            "merge_history": self.merge_history,
        }

    def export_deduplicated_entities(self, output_file: Path) -> None:
        """
        Export deduplicated entities to a JSON file.
        
        Args:
            output_file: Path where to save the deduplicated entities
        """
        entities = []
        for entity in self.entities_by_id.values():
            # Remove internal tracking fields
            clean_entity = {k: v for k, v in entity.items() if not k.startswith("_")}
            entities.append(clean_entity)
        
        output_data = {
            "entities": entities,
            "metadata": {
                "total_entities": len(entities),
                "deduplication_performed": True,
            }
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(entities)} deduplicated entities to {output_file}")

    def export_merge_report(self, output_file: Path) -> None:
        """
        Export merge report to a JSON file.
        
        Args:
            output_file: Path where to save the merge report
        """
        report = self.get_merge_report()
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Exported merge report to {output_file}")
        print(f"\nMerge Summary:")
        print(f"  Total Entities: {report['total_entities']}")
        print(f"  Merged Entities: {report['merged_entities']}")
        print(f"  New Entities: {report['new_entities']}")
        print(f"  Merge Operations: {report['merge_operations']}")
