from __future__ import annotations

import re
from typing import Iterable, List, Sequence, Set, Tuple

from core import GraphData, GraphNode, GraphRelationship

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return _TOKEN_PATTERN.findall(text.lower())


def _collect_node_tokens(node: GraphNode) -> Set[str]:
    tokens: Set[str] = set()
    tokens.update(_tokenize(node.key))
    for label in node.labels:
        tokens.update(_tokenize(label))
    for value in node.properties.values():
        if isinstance(value, str):
            tokens.update(_tokenize(value))
    return tokens


def _score_node(node: GraphNode, question_tokens: Set[str], question_text: str) -> int:
    if not question_tokens:
        return 0
    node_tokens = _collect_node_tokens(node)
    score = len(question_tokens & node_tokens)
    name = node.properties.get("name")
    if isinstance(name, str) and name:
        lowered = name.lower()
        if question_text in lowered:
            score += max(1, len(question_tokens))
    section = node.properties.get("section")
    if isinstance(section, str) and section:
        section_tokens = set(_tokenize(section))
        score += len(section_tokens & question_tokens)
    return score


def _summarize_node(node: GraphNode) -> str:
    name = node.properties.get("name")
    display = node.key
    if isinstance(name, str) and name and name.lower() != node.key.lower():
        display = f"{display} / {name}"
    label_set = [label for label in node.labels if label != "GraphNode"]
    props = {
        key: value
        for key, value in node.properties.items()
        if key != "uid" and value is not None and key != "name"
    }
    pieces: List[str] = [display]
    if label_set:
        pieces.append(f"labels={','.join(label_set)}")
    if props:
        prop_parts = [f"{key}={value}" for key, value in sorted(props.items())]
        pieces.append(f"props={'; '.join(prop_parts)}")
    return " | ".join(pieces)


def _summarize_relationship(rel: GraphRelationship) -> str:
    props = ", ".join(
        f"{key}={value}"
        for key, value in sorted(rel.properties.items())
        if value is not None
    )
    base = f"{rel.start_key} -[{rel.rel_type}]-> {rel.end_key}"
    return f"{base} ({props})" if props else base


def _build_context_section(title: str, lines: Iterable[str]) -> List[str]:
    entries = [line for line in lines if line]
    if not entries:
        return []
    section_lines = [title]
    section_lines.extend(f"- {entry}" for entry in entries)
    return section_lines


def prepare_context(
    graph: GraphData,
    question: str,
    *,
    top_k_nodes: int,
    max_neighbor_nodes: int,
    relationship_limit: int,
) -> Tuple[str, List[GraphNode], List[GraphNode], List[GraphRelationship]]:
    question_tokens = set(_tokenize(question))
    question_lower = question.strip().lower()
    scored_nodes: List[Tuple[int, int, GraphNode]] = []
    for index, node in enumerate(graph.nodes.values()):
        score = _score_node(node, question_tokens, question_lower)
        scored_nodes.append((score, index, node))
    scored_nodes.sort(key=lambda item: (-item[0], item[1]))

    primary_nodes: List[GraphNode] = [
        node for score, _, node in scored_nodes if score > 0
    ][:top_k_nodes]
    if not primary_nodes:
        primary_nodes = [node for _, _, node in scored_nodes[:top_k_nodes]]

    primary_keys = [node.key for node in primary_nodes]
    selected_keys: List[str] = list(primary_keys)
    selected_key_set: Set[str] = set(primary_keys)

    neighbor_keys: List[str] = []
    if max_neighbor_nodes > 0:
        for rel in graph.relationships:
            if rel.start_key in selected_key_set or rel.end_key in selected_key_set:
                for candidate in (rel.start_key, rel.end_key):
                    if candidate not in selected_key_set and candidate not in neighbor_keys:
                        neighbor_keys.append(candidate)
                        if len(neighbor_keys) >= max_neighbor_nodes:
                            break
            if len(neighbor_keys) >= max_neighbor_nodes:
                break
    neighbor_nodes = [graph.nodes[key] for key in neighbor_keys if key in graph.nodes]
    selected_keys.extend(key for key in neighbor_keys if key in graph.nodes)
    selected_key_set.update(selected_keys)

    relevant_relationships: List[GraphRelationship] = []
    for rel in graph.relationships:
        if rel.start_key in selected_key_set and rel.end_key in selected_key_set:
            relevant_relationships.append(rel)
            if len(relevant_relationships) >= relationship_limit:
                break

    context_lines: List[str] = []
    context_lines.extend(
        _build_context_section(
            "Primary nodes",
            (_summarize_node(node) for node in primary_nodes),
        )
    )
    context_lines.extend(
        _build_context_section(
            "Connected context nodes",
            (_summarize_node(node) for node in neighbor_nodes),
        )
    )
    context_lines.extend(
        _build_context_section(
            "Relevant relationships",
            (_summarize_relationship(rel) for rel in relevant_relationships),
        )
    )
    context = "\n".join(context_lines) if context_lines else "No knowledge graph context available."
    return context, primary_nodes, neighbor_nodes, relevant_relationships


__all__ = ["prepare_context"]
