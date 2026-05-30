"""OpenAI provider — optional cloud backend.

Install: uv add 'eci-llm[openai]'

Also powers OpenRouterProvider (same API surface, different base URL).
"""

from __future__ import annotations

import time
from typing import Any

from eci_llm.errors import LLMProviderError, LLMProviderNotAvailable
from eci_llm.protocol import (
    EmbeddingRequest,
    EmbeddingResponse,
    LLMRequest,
    LLMResponse,
)


def _require_openai() -> Any:
    try:
        import openai  # type: ignore[import-not-found]

        return openai
    except ImportError as exc:
        raise LLMProviderNotAvailable(
            "openai package is not installed. Run: uv add 'eci-llm[openai]'"
        ) from exc


class OpenAIProvider:
    """OpenAI chat completions. Accepts an optional base_url for compatible APIs."""

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        openai = _require_openai()
        kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = openai.OpenAI(**kwargs)
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, request: LLMRequest) -> LLMResponse:
        messages: list[dict[str, str]] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.extend({"role": m.role, "content": m.content} for m in request.messages)

        t0 = time.monotonic()
        try:
            resp = self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except Exception as exc:
            raise LLMProviderError(f"OpenAI API error: {exc}") from exc
        latency_ms = (time.monotonic() - t0) * 1000.0
        choice = resp.choices[0]
        usage = resp.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=resp.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms,
        )


class OpenAIEmbeddingProvider:
    """OpenAI embeddings API."""

    def __init__(self, api_key: str, model: str, dimensions: int) -> None:
        openai = _require_openai()
        self._client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        try:
            resp = self._client.embeddings.create(  # type: ignore[union-attr]
                model=self._model, input=request.texts
            )
        except Exception as exc:
            raise LLMProviderError(f"OpenAI embeddings error: {exc}") from exc
        usage = resp.usage
        return EmbeddingResponse(
            embeddings=[item.embedding for item in resp.data],
            model=self._model,
            total_tokens=usage.total_tokens if usage else 0,
        )
