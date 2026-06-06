"""AssistantService — retrieval-augmented answers, citation-grounded and fail-closed.

Invariant (AP-2, evidence before inference): if retrieval yields zero citations,
the LLM is never called. The assistant only synthesises from numbered context and is
instructed to cite ``[n]`` and to say so when the context is insufficient.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator

from eci_llm.protocol import (
    LLMMessage,
    LLMProvider,
    LLMRequest,
    StreamingLLMProvider,
)
from eci_observability import get_logger

from eci_retrieval.dto import (
    AssistantAnswer,
    Citation,
    RetrievalRequest,
    RetrievalResult,
)
from eci_retrieval.hybrid_retriever import HybridRetriever

_log = get_logger("eci_retrieval.assistant")

_SYSTEM_PROMPT = (
    "You are ECI's grounded engineering assistant. Answer ONLY from the numbered "
    "context below. Cite the sources you use inline as [1], [2], etc. If the context "
    "does not contain the answer, say so plainly — do not speculate or use outside "
    "knowledge."
)


class AssistantService:
    """Per-call instance; orchestrates retrieval + grounded generation."""

    def __init__(self, retriever: HybridRetriever, provider: LLMProvider) -> None:
        self._retriever = retriever
        self._provider = provider

    def retrieve(self, query: str, top_k: int, tenant_id: uuid.UUID | None) -> RetrievalResult:
        return self._retriever.retrieve(
            RetrievalRequest(query=query, top_k=top_k, tenant_id=tenant_id)
        )

    def ask(self, query: str, top_k: int, tenant_id: uuid.UUID | None) -> AssistantAnswer:
        """Full (non-streaming) grounded answer. Fail-closed when no citations."""
        result = self.retrieve(query, top_k, tenant_id)
        if not result.has_citations:
            return AssistantAnswer(query=query, answer=None, has_citations=False, citations=[])
        answer = self._provider.complete(self._build_request(query, result.citations))
        return AssistantAnswer(
            query=query,
            answer=answer.content,
            has_citations=True,
            citations=result.citations,
        )

    def stream_answer(self, query: str, citations: list[Citation]) -> Iterator[str]:
        """Yield answer deltas. Callers MUST gate on ``has_citations`` first."""
        if not citations:
            raise ValueError("stream_answer requires non-empty citations (fail-closed)")
        request = self._build_request(query, citations)
        if isinstance(self._provider, StreamingLLMProvider):
            yield from self._provider.stream_complete(request)
        else:
            yield self._provider.complete(request).content

    def _build_request(self, query: str, citations: list[Citation]) -> LLMRequest:
        context = "\n\n".join(
            f"[{i + 1}] {c.title or c.source_uri or c.source_type}\n{c.content}"
            for i, c in enumerate(citations)
        )
        user = f"Context:\n{context}\n\nQuestion: {query}"
        return LLMRequest(
            messages=[LLMMessage(role="user", content=user)],
            system=_SYSTEM_PROMPT,
        )
