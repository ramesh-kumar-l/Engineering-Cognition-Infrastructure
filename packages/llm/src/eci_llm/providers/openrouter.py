"""OpenRouter provider — routes to 100+ models via an OpenAI-compatible API.

Install: uv add 'eci-llm[openai]'  (reuses the OpenAI SDK)
"""

from __future__ import annotations

from eci_llm.providers.openai import OpenAIProvider

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(OpenAIProvider):
    """Thin subclass that points the OpenAI client at OpenRouter's base URL."""

    def __init__(self, api_key: str, model: str) -> None:
        super().__init__(api_key=api_key, model=model, base_url=_OPENROUTER_BASE_URL)
