"""Unit tests for LLM protocol DTOs and Protocol structural checks."""

from __future__ import annotations

from eci_llm.protocol import (
    EmbeddingProvider,
    EmbeddingRequest,
    EmbeddingResponse,
    LLMMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)


def test_llm_message_fields() -> None:
    msg = LLMMessage(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"


def test_llm_request_defaults() -> None:
    req = LLMRequest(messages=[LLMMessage("user", "hi")])
    assert req.max_tokens == 2048
    assert req.temperature == 0.1
    assert req.system is None


def test_llm_response_defaults() -> None:
    resp = LLMResponse(content="answer", model="llama3.2")
    assert resp.prompt_tokens == 0
    assert resp.completion_tokens == 0
    assert resp.latency_ms == 0.0


def test_embedding_request() -> None:
    req = EmbeddingRequest(texts=["hello", "world"])
    assert len(req.texts) == 2


def test_embedding_response_defaults() -> None:
    resp = EmbeddingResponse(embeddings=[[0.1, 0.2]], model="nomic-embed-text")
    assert resp.total_tokens == 0


class _StubLLM:
    @property
    def model_name(self) -> str:
        return "stub"

    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content="ok", model="stub")


class _StubEmbedder:
    @property
    def model_name(self) -> str:
        return "stub-embed"

    @property
    def dimensions(self) -> int:
        return 4

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(
            embeddings=[[0.0] * 4 for _ in request.texts],
            model="stub-embed",
        )


def test_llm_provider_protocol_runtime_check() -> None:
    stub = _StubLLM()
    assert isinstance(stub, LLMProvider)


def test_embedding_provider_protocol_runtime_check() -> None:
    stub = _StubEmbedder()
    assert isinstance(stub, EmbeddingProvider)
    assert stub.dimensions == 4


def test_llm_provider_complete() -> None:
    stub = _StubLLM()
    resp = stub.complete(LLMRequest(messages=[LLMMessage("user", "hi")]))
    assert resp.content == "ok"
    assert resp.model == "stub"


def test_embedding_provider_embed() -> None:
    stub = _StubEmbedder()
    resp = stub.embed(EmbeddingRequest(texts=["a", "b"]))
    assert len(resp.embeddings) == 2
    assert len(resp.embeddings[0]) == 4
