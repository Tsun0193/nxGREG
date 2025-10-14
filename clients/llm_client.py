from __future__ import annotations

import os
from typing import Optional

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


if __name__ == "__main__":
    prompt = "Hello"
    print(generate_response(prompt))
