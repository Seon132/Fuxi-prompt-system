"""
LLM call wrapper — supports any OpenAI-compatible API.
"""

from __future__ import annotations

import os
from pathlib import Path

from openai import AsyncOpenAI

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=os.getenv("LLM_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        )
    return _client


def get_model() -> str:
    return os.getenv("LLM_MODEL", "gpt-4o")


async def chat(
    system: str,
    user: str,
    model: str | None = None,
    temperature: float = 0.3,
) -> str:
    client = get_client()
    resp = await client.chat.completions.create(
        model=model or get_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def load_prompt(name: str) -> str:
    """Load a prompt file from the prompts/ directory."""
    prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
    path = prompts_dir / f"{name}.md"
    return path.read_text(encoding="utf-8")
