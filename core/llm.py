"""
core/llm.py

ONE job: send a prompt to Groq (Llama) and return text.
"""

from __future__ import annotations

try:
    from recruitai import config
except ImportError:  # pragma: no cover - supports running this module from repo root.
    import config  # type: ignore[no-redef]


_client = None  # lazy singleton.


def _get_client():
    global _client
    if _client is None:
        if not config.GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and paste your "
                "free Groq key from https://console.groq.com/keys"
            )
        from groq import Groq

        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def generate(system: str, user: str) -> str:
    """Send a system + user prompt to Groq and return the model's text reply."""
    client = _get_client()
    response = client.chat.completions.create(
        model=config.GROQ_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (response.choices[0].message.content or "").strip()
