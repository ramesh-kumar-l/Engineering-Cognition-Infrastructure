"""LLM and Embedding provider protocols + request/response DTOs."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class LLMMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class LLMRequest:
    messages: list[LLMMessage]
    max_tokens: int = 2048
    temperature: float = 0.1
    system: str | None = None


@dataclass
class LLMResponse:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0


@dataclass
class EmbeddingRequest:
    texts: list[str]


@dataclass
class EmbeddingResponse:
    embeddings: list[list[float]]
    model: str
    total_tokens: int = 0


@runtime_checkable
class LLMProvider(Protocol):
    """Synchronous LLM completion provider."""

    @property
    def model_name(self) -> str: ...

    def complete(self, request: LLMRequest) -> LLMResponse: ...


@runtime_checkable
class StreamingLLMProvider(Protocol):
    """Optional capability: incremental token streaming.

    Kept separate from ``LLMProvider`` so providers that only support buffered
    completion (and the callers that only need it) are unaffected. Callers detect
    support with ``isinstance(provider, StreamingLLMProvider)``.
    """

    def stream_complete(self, request: LLMRequest) -> Iterator[str]: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Synchronous text embedding provider."""

    @property
    def model_name(self) -> str: ...

    @property
    def dimensions(self) -> int: ...

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse: ...
