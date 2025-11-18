from __future__ import annotations

import json
import logging
from typing import Any, List, Mapping, Optional, Sequence, Tuple

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

logger = logging.getLogger(__name__)


def neo4j_retriever_available() -> bool:
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


def run_text2cypher_retrieval(
    question: str,
    uri: str,
    username: str,
    password: str,
    *,
    schema: Optional[str],
    examples: Optional[Sequence[str]],
    model_name: str,
) -> Tuple[str, str, Optional[str]]:
    if not neo4j_retriever_available():
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


__all__ = [
    "neo4j_retriever_available",
    "run_text2cypher_retrieval",
]
