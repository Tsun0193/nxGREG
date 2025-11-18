from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Sequence

from clients import generate_response
from data import resolve_input_path
from loading import Neo4jLoader
from parsing import KnowledgeGraphParser
from tqdm import tqdm

from .rag_components import (
    KnowledgeGraphRAGResult,
    RAG_PROMPT_TEMPLATE,
    neo4j_retriever_available,
    prepare_context,
    run_text2cypher_retrieval,
)

logger = logging.getLogger(__name__)


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
        and neo4j_retriever_available()
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
        context, primary_nodes, neighbor_nodes, relationships = prepare_context(
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
                retriever_answer, retriever_context, generated_query = run_text2cypher_retrieval(
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
