from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class GraphNode:
    key: str
    labels: Tuple[str, ...]
    properties: Dict[str, Optional[str]] = field(default_factory=dict)


@dataclass
class GraphRelationship:
    start_key: str
    end_key: str
    rel_type: str
    properties: Dict[str, Optional[str]] = field(default_factory=dict)


class GraphData:
    """Container for nodes and relationships destined for Neo4j."""

    def __init__(self) -> None:
        self.nodes: Dict[str, GraphNode] = {}
        self.relationships: List[GraphRelationship] = []
        self._relationship_keys: set[Tuple[str, str, str]] = set()

    def add_node(self, key: str, labels: Iterable[str], **properties: Optional[str]) -> None:
        label_tuple = tuple(sorted(set(["GraphNode", *labels])))
        if key in self.nodes:
            existing = self.nodes[key]
            existing.labels = tuple(sorted(set(existing.labels + label_tuple)))
            for prop_key, value in properties.items():
                if value is not None:
                    existing.properties[prop_key] = value
        else:
            props = {k: v for k, v in properties.items() if v is not None}
            props["uid"] = key
            self.nodes[key] = GraphNode(key=key, labels=label_tuple, properties=props)

    def add_relationship(
        self,
        start_key: str,
        end_key: str,
        rel_type: str,
        **properties: Optional[str],
    ) -> None:
        rel_key = (start_key, end_key, rel_type)
        if rel_key in self._relationship_keys:
            return
        props = {k: v for k, v in properties.items() if v is not None}
        self.relationships.append(
            GraphRelationship(
                start_key=start_key,
                end_key=end_key,
                rel_type=rel_type,
                properties=props,
            )
        )
        self._relationship_keys.add(rel_key)
