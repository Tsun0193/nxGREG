from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover - optional dependency
    GraphDatabase = None  # type: ignore[assignment]

try:
    from neo4j_graphrag.llm import OpenAILLM
    from neo4j_graphrag.retrievers import Text2CypherRetriever
except ImportError:  # pragma: no cover - optional dependency
    OpenAILLM = None  # type: ignore[assignment]
    Text2CypherRetriever = None  # type: ignore[assignment]

from clients import generate_response
from core import GraphData, GraphNode, GraphRelationship
from data import resolve_input_path
from loading import Neo4jLoader
from parsing import KnowledgeGraphParser
from tqdm import tqdm

logger = logging.getLogger(__name__)

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

RAG_PROMPT_TEMPLATE = """You are a senior architect helping a teammate reason about a system.
Use the supplied knowledge graph context to answer the user question. Prefer precise, actionable language
that references the graph nodes or relationships when relevant. If the context does not contain the answer,
reply with that limitation and suggest which parts of the graph to inspect.

Context:
{context}

Question:
{question}

Compose a concise answer with short sections or bullet points when it helps clarity."""


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


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    return _TOKEN_PATTERN.findall(text.lower())


def _neo4j_retriever_available() -> bool:
    return all(
        dependency is not None
        for dependency in (GraphDatabase, Text2CypherRetriever, OpenAILLM)
    )


def _stringify_section(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Mapping):
        try:
            return json.dumps(value, indent=2, default=str)
        except TypeError:
            return str(value)
    if isinstance(value, (list, tuple, set)):
        parts = [part for part in (_stringify_section(item) for item in value) if part]
        return "\n".join(parts)
    return str(value)


def _normalize_retriever_output(result: Any) -> Tuple[str, str, Optional[str]]:
    """
    Best-effort extraction of answer, context, and generated Cypher from retriever output.
    Falls back to string representations when structured data is unavailable.
    """

    cypher_query: Optional[str] = None
    answer_text: Optional[str] = None
    context_fragments: List[str] = []

    def _extract_from_mapping(mapping: Mapping[str, Any]) -> None:
        nonlocal cypher_query, answer_text
        query_keys = ("generated_cypher", "cypher", "cypher_query", "query")
        answer_keys = (
            "final_response",
            "response",
            "answer",
            "output",
            "result",
            "message",
            "text",
        )
        context_keys = (
            "context",
            "retrieved_context",
            "results",
            "records",
            "data",
            "graph",
            "table",
        )
        for key in query_keys:
            value = mapping.get(key)
            if isinstance(value, str) and value.strip():
                cypher_query = value.strip()
                break
        if answer_text is None:
            for key in answer_keys:
                value = mapping.get(key)
                if isinstance(value, str) and value.strip():
                    answer_text = value.strip()
                    break
        for key in context_keys:
            value = mapping.get(key)
            if value:
                fragment = _stringify_section(value)
                if fragment:
                    context_fragments.append(fragment)

    processed = False
    if result is None:
        processed = True
    elif isinstance(result, Mapping):
        _extract_from_mapping(result)
        processed = True
    elif hasattr(result, "model_dump"):
        try:
            dumped = result.model_dump()
        except Exception:  # pragma: no cover - defensive
            dumped = None
        if isinstance(dumped, Mapping):
            _extract_from_mapping(dumped)
            processed = True
    if not processed and hasattr(result, "__dict__"):
        mapping = {
            key: value
            for key, value in vars(result).items()
            if not key.startswith("_")
        }
        _extract_from_mapping(mapping)
        processed = True
    if not processed:
        # As a final fallback, convert to string for both answer and context.
        answer_text = str(result).strip()
        context_fragments.append(answer_text)

    context_text = "\n\n".join(fragment for fragment in context_fragments if fragment)

    if cypher_query and (cypher_query not in context_text):
        prefix = f"Generated Cypher Query:\n{cypher_query}"
        context_text = f"{prefix}\n\n{context_text}" if context_text else prefix

    if answer_text is None:
        answer_text = context_text or ""
    if not context_text:
        context_text = answer_text

    return answer_text, context_text, cypher_query


def _run_text2cypher_retrieval(
    question: str,
    uri: str,
    username: str,
    password: str,
    *,
    schema: Optional[str],
    examples: Optional[Sequence[str]],
    model_name: str,
) -> Tuple[str, str, Optional[str]]:
    if not _neo4j_retriever_available():
        raise RuntimeError(
            "neo4j and neo4j-graphrag must be installed to use Text2Cypher retrieval."
        )
    assert GraphDatabase is not None
    assert Text2CypherRetriever is not None
    assert OpenAILLM is not None

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        llm = OpenAILLM(model_name=model_name)
        normalized_examples: Optional[List[str]] = None
        if examples:
            if isinstance(examples, str):
                normalized_examples = [examples]
            else:
                normalized_examples = list(examples)
        retriever = Text2CypherRetriever(
            driver=driver,
            llm=llm,
            neo4j_schema=schema,
            examples=normalized_examples,
        )
        raw_result = retriever.search(query_text=question)
        return _normalize_retriever_output(raw_result)
    finally:
        driver.close()

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


def _prepare_context(
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


def run_knowledge_graph_rag_pipeline(
    question: str,
    readme_path: Optional[Path] = None,
    *,
    top_k_nodes: int = 6,
    max_neighbor_nodes: int = 12,
    relationship_limit: int = 24,
    wipe: bool = False,
    neo4j_url: Optional[str] = None,
    neo4j_username: Optional[str] = None,
    neo4j_password: Optional[str] = None,
    neo4j_schema: Optional[str] = None,
    retriever_examples: Optional[Sequence[str]] = None,
    retriever_model_name: str = "gpt-3.5-turbo",
    use_text2cypher: bool = True,
) -> KnowledgeGraphRAGResult:
    """
    Execute a retrieval-augmented generation flow backed by the knowledge graph parser.

    The pipeline parses the README into a knowledge graph, selects the most relevant nodes/relationships
    for the provided question, and answers via either the local RAG prompt or the Neo4j Text2Cypher retriever.
    When Neo4j credentials are supplied, the parsed graph is loaded (optionally wiping the existing database
    first). If neo4j-graphrag is installed, the pipeline can connect to Neo4j and execute Text2Cypher retrieval
    using the supplied OpenAI model.
    """
    if not question or not question.strip():
        raise ValueError("question must be a non-empty string.")

    should_load = bool(neo4j_url and neo4j_username and neo4j_password)
    can_use_text2cypher = (
        use_text2cypher
        and should_load
        and _neo4j_retriever_available()
    )

    steps: List[str] = [
        "Resolve input",
        "Parse input",
        "Select graph context",
        "Load graph into Neo4j" if should_load else "Skip Neo4j load",
    ]
    if can_use_text2cypher:
        steps.append("Run Text2Cypher retrieval")
        steps.append("Request completion (fallback)")
    else:
        steps.append("Request completion")

    with tqdm(total=len(steps), desc="KG RAG pipeline", unit="step") as progress:
        def advance(step_description: str) -> None:
            progress.set_postfix_str(step_description)
            progress.update()

        advance("Resolving input")
        resolved_input, input_source = resolve_input_path(readme_path)
        if not resolved_input.exists():
            raise FileNotFoundError(f"Input file not found at {resolved_input}")
        logger.info("RAG pipeline using input (%s): %s", input_source, resolved_input)

        advance("Parsing input")
        parser = KnowledgeGraphParser(resolved_input)
        graph = parser.parse()
        logger.info("Parsed %d nodes and %d relationships", len(graph.nodes), len(graph.relationships))

        advance("Selecting graph context")
        context, primary_nodes, neighbor_nodes, relationships = _prepare_context(
            graph,
            question,
            top_k_nodes=top_k_nodes,
            max_neighbor_nodes=max_neighbor_nodes,
            relationship_limit=relationship_limit,
        )
        logger.info(
            "Context prepared with %d primary nodes, %d neighbor nodes, and %d relationships",
            len(primary_nodes),
            len(neighbor_nodes),
            len(relationships),
        )

        if should_load:
            assert neo4j_url is not None
            assert neo4j_username is not None
            assert neo4j_password is not None
            advance("Loading graph into Neo4j")
            loader = Neo4jLoader(neo4j_url, neo4j_username, neo4j_password)
            try:
                loader.load(graph, wipe=wipe)
            finally:
                loader.close()
            logger.info("Neo4j load complete")
        else:
            advance("Neo4j load skipped")
            logger.info("Neo4j connection details missing; skipping load")

        prompt = ""
        answer = ""
        cypher_query: Optional[str] = None
        cypher_context: Optional[str] = None
        needs_fallback = not can_use_text2cypher

        if can_use_text2cypher:
            assert neo4j_url is not None
            assert neo4j_username is not None
            assert neo4j_password is not None
            advance("Running Text2Cypher retrieval")
            try:
                retriever_answer, retriever_context, generated_query = _run_text2cypher_retrieval(
                    question=question.strip(),
                    uri=neo4j_url,
                    username=neo4j_username,
                    password=neo4j_password,
                    schema=neo4j_schema,
                    examples=retriever_examples,
                    model_name=retriever_model_name,
                )
                answer = retriever_answer
                cypher_context = retriever_context
                cypher_query = generated_query
                if cypher_context:
                    context = cypher_context
                needs_fallback = not bool(answer.strip())
                logger.info("Text2Cypher retrieval completed using model %s", retriever_model_name)
            except Exception as exc:  # pragma: no cover - depends on external services
                needs_fallback = True
                logger.exception("Text2Cypher retrieval failed: %s", exc)

        fallback_label = "Request completion (fallback)" if can_use_text2cypher else "Request completion"
        if needs_fallback:
            advance(fallback_label)
            prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=question.strip())
            answer = generate_response(prompt)
            logger.info("LLM response received (%d characters)", len(answer))
        else:
            advance(f"{fallback_label} skipped")

    return KnowledgeGraphRAGResult(
        question=question.strip(),
        answer=answer,
        prompt=prompt,
        context=context,
        primary_node_ids=[node.key for node in primary_nodes],
        neighbor_node_ids=[node.key for node in neighbor_nodes],
        relationship_keys=[(rel.start_key, rel.end_key, rel.rel_type) for rel in relationships],
        graph=graph,
        cypher_query=cypher_query,
        cypher_context=cypher_context,
    )


__all__ = ["KnowledgeGraphRAGResult", "run_knowledge_graph_rag_pipeline"]
