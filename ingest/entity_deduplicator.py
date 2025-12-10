"""Entity deduplication module for merging duplicate entities based on ID and properties."""

from __future__ import annotations

from typing import Dict, List, Any, Set
from pathlib import Path


class EntityDeduplicator:
    """
    Handles deduplication of entities by merging duplicates based on entity ID.
    
    When multiple entities with the same ID are encountered, this class will:
    - Merge their properties intelligently
    - Track which source files contributed to the merged entity
    - Maintain a history of merge operations
    """

    def __init__(self):
        """Initialize the deduplicator."""
        self.entities: Dict[str, Dict[str, Any]] = {}  # Maps entity ID to merged entity
        self.merge_history: List[Dict[str, Any]] = []  # Track all merge operations
        self.source_tracking: Dict[str, Set[str]] = {}  # Maps entity ID to source files

    def add_entity(self, entity: Dict[str, Any], source_file: str) -> None:
        """
        Add an entity to the deduplicator, merging if duplicate ID exists.

        Args:
            entity: Entity dictionary with 'id', 'type', and other properties
            source_file: Name of the source file this entity came from
        """
        entity_id = entity.get("id")
        if not entity_id:
            return

        # Track source file
        if entity_id not in self.source_tracking:
            self.source_tracking[entity_id] = set()
        self.source_tracking[entity_id].add(source_file)

        # If this is the first time seeing this entity, store it
        if entity_id not in self.entities:
            self.entities[entity_id] = entity.copy()
            return

        # Entity exists - merge properties
        existing = self.entities[entity_id]
        merged = self._merge_entities(existing, entity)

        # Track the merge operation
        self.merge_history.append({
            "entity_id": entity_id,
            "source_file": source_file,
            "existing_sources": list(self.source_tracking[entity_id]),
            "merged_properties": list(merged.keys()),
        })

        self.entities[entity_id] = merged

    def _merge_entities(
        self,
        existing: Dict[str, Any],
        new: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Merge two entities with the same ID, combining their properties.

        Merge strategy:
        - Keep all non-empty values
        - For conflicts, prefer non-empty new values over existing
        - For lists, combine and deduplicate
        - For strings, prefer longer/more detailed version

        Args:
            existing: The existing entity
            new: The new entity to merge in

        Returns:
            Merged entity dictionary
        """
        merged = existing.copy()

        for key, new_value in new.items():
            if key not in merged or not merged[key]:
                # Key doesn't exist or is empty in existing - use new value
                merged[key] = new_value
            elif not new_value:
                # New value is empty - keep existing
                continue
            elif key == "id":
                # ID should always be the same
                continue
            elif key == "type":
                # Type should be consistent, but prefer new if different
                if merged[key] != new_value:
                    print(f"Warning: Type mismatch for entity {merged.get('id')}: "
                          f"{merged[key]} vs {new_value}. Keeping existing.")
            elif isinstance(new_value, list) and isinstance(merged[key], list):
                # Merge lists and deduplicate
                merged[key] = self._merge_lists(merged[key], new_value)
            elif isinstance(new_value, str) and isinstance(merged[key], str):
                # For strings, prefer longer/more detailed version
                if len(new_value) > len(merged[key]):
                    merged[key] = new_value
            elif isinstance(new_value, dict) and isinstance(merged[key], dict):
                # Recursively merge nested dictionaries
                merged[key] = self._merge_dicts(merged[key], new_value)
            else:
                # For other types, prefer new value if different
                if merged[key] != new_value:
                    merged[key] = new_value

        return merged

    @staticmethod
    def _merge_lists(list1: List[Any], list2: List[Any]) -> List[Any]:
        """
        Merge two lists, removing duplicates while preserving order.

        Args:
            list1: First list
            list2: Second list

        Returns:
            Merged list with duplicates removed
        """
        # Use dict to maintain order while removing duplicates
        seen = {}
        for item in list1 + list2:
            # Use JSON representation for complex types
            if isinstance(item, (dict, list)):
                key = str(item)
            else:
                key = item
            if key not in seen:
                seen[key] = item

        return list(seen.values())

    @staticmethod
    def _merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.

        Args:
            dict1: First dictionary
            dict2: Second dictionary

        Returns:
            Merged dictionary
        """
        merged = dict1.copy()

        for key, value in dict2.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = EntityDeduplicator._merge_dicts(merged[key], value)
            elif isinstance(value, list) and isinstance(merged[key], list):
                merged[key] = EntityDeduplicator._merge_lists(merged[key], value)
            else:
                # Prefer non-empty new values
                if value:
                    merged[key] = value

        return merged

    def get_entity(self, entity_id: str) -> Dict[str, Any] | None:
        """
        Get a deduplicated entity by ID.

        Args:
            entity_id: The entity ID

        Returns:
            The merged entity, or None if not found
        """
        return self.entities.get(entity_id)

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """
        Get all deduplicated entities.

        Returns:
            List of all merged entities
        """
        return list(self.entities.values())

    def get_merge_report(self) -> Dict[str, Any]:
        """
        Generate a report on deduplication operations.

        Returns:
            Dictionary containing merge statistics
        """
        return {
            "total_entities": len(self.entities),
            "merged_entities": len(self.merge_history),
            "new_entities": len(self.entities) - len(self.merge_history),
            "merge_operations": len(self.merge_history),
            "entities_with_multiple_sources": sum(
                1 for sources in self.source_tracking.values() if len(sources) > 1
            ),
        }

    def get_source_files(self, entity_id: str) -> Set[str]:
        """
        Get all source files that contributed to an entity.

        Args:
            entity_id: The entity ID

        Returns:
            Set of source file names
        """
        return self.source_tracking.get(entity_id, set())

    def print_merge_report(self) -> None:
        """Print a detailed merge report."""
        report = self.get_merge_report()

        print("\n=== Entity Deduplication Report ===")
        print(f"Total Unique Entities: {report['total_entities']}")
        print(f"New Entities: {report['new_entities']}")
        print(f"Merged Entities: {report['merged_entities']}")
        print(f"Merge Operations: {report['merge_operations']}")
        print(f"Entities from Multiple Sources: {report['entities_with_multiple_sources']}")

        if self.merge_history:
            print("\n=== Recent Merge Operations ===")
            for i, merge in enumerate(self.merge_history[-5:], 1):
                print(f"{i}. Entity: {merge['entity_id']}")
                print(f"   Source: {merge['source_file']}")
                print(f"   Previous Sources: {', '.join(merge['existing_sources'])}")
                print(f"   Merged Properties: {len(merge['merged_properties'])}")
