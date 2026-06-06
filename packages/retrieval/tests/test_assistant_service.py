"""Unit tests for AssistantService — fail-closed gate + streaming fallback.

No DB and no Ollama: the retriever and providers are fakes. The point is to prove
the grounding invariant (AP-2): no citations → the LLM is never invoked.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

from eci_llm.protocol import LLMRequest, LLMResponse
from eci_retrieval.assistant_service import AssistantService
from eci_retrieval.dto import Citation, RetrievalResult


def _citation(i: int) -> Citation:
    return Citation(
        source_type="document",
        source_id=uuid.uuid4(),
        chunk_index=i,
        content=f"chunk {i}",
        score=1.0 - i * 0.1,
        title=f"Doc {i}",
        source_uri=None,
    )


class FakeRetriever:
    def __init__(self, citations: list[Citation]) -> None:
        self._citations = citations
        self.calls = 0

    def retrieve(self, request: object) -> RetrievalResult:
        self.calls += 1
        return RetrievalResult(query="q", citations=self._citations, retrieval_stages={})


class RecordingProvider:
    """Buffered-only provider. Records whether complete() was called."""

    def __init__(self) -> None:
        self.complete_calls = 0

    @property
    def model_name(self) -> str:
        return "fake"

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.complete_calls += 1
        return LLMResponse(content="grounded answer [1]", model="fake")


class StreamingProvider(RecordingProvider):
    def stream_complete(self, request: LLMRequest) -> Iterator[str]:
        yield from ["gro", "unded ", "answer [1]"]


def test_ask_fail_closed_does_not_invoke_llm() -> None:
    retriever = FakeRetriever([])
    provider = RecordingProvider()
    svc = AssistantService(retriever, provider)  # type: ignore[arg-type]

    result = svc.ask("why hybrid retrieval?", top_k=5, tenant_id=None)

    assert result.has_citations is False
    assert result.answer is None
    assert result.citations == []
    assert provider.complete_calls == 0  # AP-2: no evidence → no generation


def test_ask_with_citations_invokes_llm_and_returns_answer() -> None:
    citations = [_citation(0), _citation(1)]
    provider = RecordingProvider()
    svc = AssistantService(FakeRetriever(citations), provider)  # type: ignore[arg-type]

    result = svc.ask("q", top_k=5, tenant_id=None)

    assert result.has_citations is True
    assert result.answer == "grounded answer [1]"
    assert result.citations == citations
    assert provider.complete_calls == 1


def test_stream_answer_uses_streaming_provider() -> None:
    svc = AssistantService(FakeRetriever([]), StreamingProvider())  # type: ignore[arg-type]
    tokens = list(svc.stream_answer("q", [_citation(0)]))
    assert "".join(tokens) == "grounded answer [1]"
    assert len(tokens) > 1  # truly incremental


def test_stream_answer_falls_back_for_buffered_provider() -> None:
    provider = RecordingProvider()
    svc = AssistantService(FakeRetriever([]), provider)  # type: ignore[arg-type]
    tokens = list(svc.stream_answer("q", [_citation(0)]))
    assert tokens == ["grounded answer [1]"]
    assert provider.complete_calls == 1


def test_stream_answer_rejects_empty_citations() -> None:
    svc = AssistantService(FakeRetriever([]), RecordingProvider())  # type: ignore[arg-type]
    try:
        list(svc.stream_answer("q", []))
        raised = False
    except ValueError:
        raised = True
    assert raised
