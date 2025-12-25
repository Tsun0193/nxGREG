from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

_client: Optional[QdrantClient] = None


def _get_client() -> QdrantClient:
    """Initialize and return a singleton Qdrant client."""
    global _client
    if _client is None:
        load_dotenv()
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        _client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )
    return _client


def create_collection(
    collection_name: str,
    vector_size: int = 1536,
    distance: Distance = Distance.COSINE,
) -> bool:
    """
    Create a new collection in Qdrant.
    
    Args:
        collection_name: Name of the collection to create
        vector_size: Dimension of the vectors (default: 1536 for OpenAI embeddings)
        distance: Distance metric to use (COSINE, EUCLID, DOT)
    
    Returns:
        True if collection was created successfully
    """
    client = _get_client()
    
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance),
        )
        return True
    except Exception as e:
        print(f"Error creating collection: {e}")
        return False


def collection_exists(collection_name: str) -> bool:
    """Check if a collection exists."""
    client = _get_client()
    try:
        collections = client.get_collections()
        return any(col.name == collection_name for col in collections.collections)
    except Exception:
        return False


def ingest_chunks(
    collection_name: str,
    chunks: List[str],
    vectors: List[List[float]],
    metadata: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None,
) -> bool:
    """
    Ingest text chunks with their vectors into Qdrant.
    
    Args:
        collection_name: Name of the collection to ingest into
        chunks: List of text chunks to store
        vectors: List of embedding vectors corresponding to chunks
        metadata: Optional list of metadata dictionaries for each chunk
        ids: Optional list of IDs for each chunk (auto-generated if not provided)
    
    Returns:
        True if ingestion was successful
    """
    client = _get_client()
    
    if len(chunks) != len(vectors):
        raise ValueError("Number of chunks must match number of vectors")
    
    if metadata and len(metadata) != len(chunks):
        raise ValueError("Number of metadata entries must match number of chunks")
    
    # Generate IDs if not provided
    if ids is None:
        ids = [str(uuid4()) for _ in range(len(chunks))]
    
    # Prepare points for insertion
    points = []
    for i, (chunk_id, chunk, vector) in enumerate(zip(ids, chunks, vectors)):
        payload = {"text": chunk}
        if metadata and i < len(metadata):
            payload.update(metadata[i])
        
        points.append(
            PointStruct(
                id=chunk_id,
                vector=vector,
                payload=payload,
            )
        )
    
    try:
        client.upsert(collection_name=collection_name, points=points)
        return True
    except Exception as e:
        print(f"Error ingesting chunks: {e}")
        return False


def search_similar(
    collection_name: str,
    query_vector: List[float],
    limit: int = 5,
    score_threshold: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks in the collection.
    
    Args:
        collection_name: Name of the collection to search
        query_vector: Query embedding vector
        limit: Maximum number of results to return
        score_threshold: Minimum similarity score threshold
    
    Returns:
        List of search results with text, metadata, and scores
    """
    client = _get_client()
    
    try:
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "metadata": {k: v for k, v in result.payload.items() if k != "text"},
            }
            for result in results
        ]
    except Exception as e:
        print(f"Error searching collection: {e}")
        return []


def delete_collection(collection_name: str) -> bool:
    """Delete a collection from Qdrant."""
    client = _get_client()
    try:
        client.delete_collection(collection_name=collection_name)
        return True
    except Exception as e:
        print(f"Error deleting collection: {e}")
        return False


def get_collection_info(collection_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a collection."""
    client = _get_client()
    try:
        info = client.get_collection(collection_name=collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }
    except Exception as e:
        print(f"Error getting collection info: {e}")
        return None
