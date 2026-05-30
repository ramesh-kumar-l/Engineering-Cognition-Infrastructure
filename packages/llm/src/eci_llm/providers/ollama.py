"""Ollama provider — offline default. Uses httpx; no third-party LLM SDK required."""

from __future__ import annotations

import time

import httpx

from eci_llm.errors import LLMProviderError
from eci_llm.protocol import (
    EmbeddingRequest,
    EmbeddingResponse,
    LLMRequest,
    LLMResponse,
)


class OllamaProvider:
    """Calls Ollama /api/chat. Compatible with any model that Ollama serves."""

    def __init__(self, host: str, model: str, timeout: float = 120.0) -> None:
        self._host = host.rstrip("/")
        self._model = model
        self._client = httpx.Client(timeout=timeout)

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, request: LLMRequest) -> LLMResponse:
        messages: list[dict[str, str]] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.extend({"role": m.role, "content": m.content} for m in request.messages)

        payload: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        t0 = time.monotonic()
        try:
            resp = self._client.post(f"{self._host}/api/chat", json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Ollama HTTP error: {exc}") from exc
        data: dict[str, object] = resp.json()
        latency_ms = (time.monotonic() - t0) * 1000.0
        message = data.get("message", {})
        assert isinstance(message, dict)
        return LLMResponse(
            content=str(message.get("content", "")),
            model=str(data.get("model", self._model)),
            prompt_tokens=int(data.get("prompt_eval_count", 0)),
            completion_tokens=int(data.get("eval_count", 0)),
            latency_ms=latency_ms,
        )

    def close(self) -> None:
        self._client.close()


class OllamaEmbeddingProvider:
    """Calls Ollama /api/embeddings. Processes texts sequentially."""

    def __init__(self, host: str, model: str, dimensions: int, timeout: float = 60.0) -> None:
        self._host = host.rstrip("/")
        self._model = model
        self._dimensions = dimensions
        self._client = httpx.Client(timeout=timeout)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        result: list[list[float]] = []
        for text in request.texts:
            payload: dict[str, object] = {"model": self._model, "prompt": text}
            try:
                resp = self._client.post(f"{self._host}/api/embeddings", json=payload)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                raise LLMProviderError(f"Ollama embeddings error: {exc}") from exc
            data: dict[str, object] = resp.json()
            embedding = data.get("embedding", [])
            assert isinstance(embedding, list)
            result.append([float(v) for v in embedding])
        return EmbeddingResponse(embeddings=result, model=self._model, total_tokens=0)

    def close(self) -> None:
        self._client.close()
