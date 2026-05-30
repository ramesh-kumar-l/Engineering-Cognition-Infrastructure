"""Anthropic provider — optional cloud backend.

Install: uv add 'eci-llm[anthropic]'
"""

from __future__ import annotations

import time
from typing import Any

from eci_llm.errors import LLMProviderError, LLMProviderNotAvailable
from eci_llm.protocol import LLMRequest, LLMResponse


def _require_anthropic() -> Any:
    try:
        import anthropic  # type: ignore[import-not-found]

        return anthropic
    except ImportError as exc:
        raise LLMProviderNotAvailable(
            "anthropic package is not installed. Run: uv add 'eci-llm[anthropic]'"
        ) from exc


class AnthropicProvider:
    """Anthropic Messages API. System prompt is passed as a top-level parameter."""

    def __init__(self, api_key: str, model: str) -> None:
        anthropic = _require_anthropic()
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, request: LLMRequest) -> LLMResponse:
        # Anthropic does not accept "system" role inside the messages list.
        messages: list[dict[str, str]] = [
            {"role": m.role, "content": m.content}
            for m in request.messages
            if m.role != "system"
        ]
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": request.max_tokens,
            "messages": messages,
        }
        if request.system:
            kwargs["system"] = request.system

        t0 = time.monotonic()
        try:
            resp = self._client.messages.create(**kwargs)  # type: ignore[union-attr]
        except Exception as exc:
            raise LLMProviderError(f"Anthropic API error: {exc}") from exc
        latency_ms = (time.monotonic() - t0) * 1000.0

        content_block = resp.content[0] if resp.content else None
        text = getattr(content_block, "text", "") if content_block else ""
        usage = resp.usage
        return LLMResponse(
            content=text,
            model=resp.model,
            prompt_tokens=usage.input_tokens if usage else 0,
            completion_tokens=usage.output_tokens if usage else 0,
            latency_ms=latency_ms,
        )
