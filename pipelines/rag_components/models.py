from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from core import GraphData


@dataclass
class KnowledgeGraphRAGResult:
    """Container for the generated answer and supporting context."""

    question: str
    answer: str
    prompt: str
    context: str
    primary_node_ids: List[str]
    neighbor_node_ids: List[str]
    relationship_keys: List[Tuple[str, str, str]]
    graph: GraphData
    cypher_query: Optional[str] = None
    cypher_context: Optional[str] = None


__all__ = ["KnowledgeGraphRAGResult"]
