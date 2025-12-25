from __future__ import annotations

import os
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        load_dotenv()
        api_key = os.getenv("NXCHAT_API_KEY")
        base_url = os.getenv("NXCHAT_API")
        if not api_key or not base_url:
            raise RuntimeError("NXCHAT_API and NXCHAT_API_KEY must be set for LLM access.")
        _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client

def generate_response(prompt: str) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model="nxchat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def embed_text(text: str, model: str = "text-embedding-ada-002") -> List[float]:
    """
    Generate embeddings for input text using OpenAI's embedding API.
    
    Args:
        text: The input text to embed
        model: The embedding model to use (default: text-embedding-ada-002)
    
    Returns:
        A list of floats representing the embedding vector
    """
    client = _get_client()
    response = client.embeddings.create(
        model=model,
        input=text,
    )
    return response.data[0].embedding


def embed_texts(texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
    """
    Generate embeddings for multiple texts using OpenAI's embedding API.
    
    Args:
        texts: List of input texts to embed
        model: The embedding model to use (default: text-embedding-ada-002)
    
    Returns:
        A list of embedding vectors
    """
    client = _get_client()
    response = client.embeddings.create(
        model=model,
        input=texts,
    )
    return [item.embedding for item in response.data]


if __name__ == "__main__":
    prompt = "Hello"
    print(generate_response(prompt))
