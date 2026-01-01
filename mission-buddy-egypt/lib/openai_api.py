from __future__ import annotations
from typing import Dict, List
from openai import OpenAI

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()  # reads OPENAI_API_KEY from env
    return _client

def chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.4,
    max_tokens: int = 550,
) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content or ""
