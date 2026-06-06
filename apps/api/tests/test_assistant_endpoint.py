"""API tests for the assistant router — JSON + SSE framing, fail-closed branch.

The AssistantService is faked (overridden) so these tests need neither Ollama nor a
populated corpus; they exercise the router contract only.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from eci_api.auth import get_request_context
from eci_api.dependencies import get_assistant_service, get_db
from eci_api.main import create_app
from eci_identity.dto import RequestContext
from eci_retrieval.dto import AssistantAnswer, Citation, RetrievalResult
from fastapi.testclient import TestClient


def _citation() -> Citation:
    return Citation(
        source_type="document",
        source_id=uuid.uuid4(),
        chunk_index=0,
        content="evidence",
        score=0.9,
        title="Doc",
        source_uri=None,
    )


class FakeAssistant:
    def __init__(self, citations: list[Citation]) -> None:
        self._citations = citations

    def retrieve(self, query: str, top_k: int, tenant_id: object) -> RetrievalResult:
        return RetrievalResult(query=query, citations=self._citations, retrieval_stages={})

    def ask(self, query: str, top_k: int, tenant_id: object) -> AssistantAnswer:
        if not self._citations:
            return AssistantAnswer(query=query, answer=None, has_citations=False, citations=[])
        return AssistantAnswer(
            query=query, answer="answer [1]", has_citations=True, citations=self._citations
        )

    def stream_answer(self, query: str, citations: list[Citation]) -> Iterator[str]:
        yield from ["ans", "wer [1]"]


def _client(api_session, tmp_path: Path, monkeypatch, fake: FakeAssistant) -> TestClient:
    import eci_ingest.blob_store as bs
    from eci_ingest.blob_store import LocalBlobStore

    monkeypatch.setattr(bs, "_STORE", LocalBlobStore(tmp_path / "blobs"))
    app = create_app()

    def _override_db():
        yield api_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_request_context] = lambda: RequestContext(
        user_id=uuid.uuid4(), tenant_id=uuid.uuid4(), role="admin", actor="t"
    )
    app.dependency_overrides[get_assistant_service] = lambda: fake
    return TestClient(app)


@pytest.mark.integration
def test_ask_with_citations(api_session, tmp_path, monkeypatch) -> None:
    with _client(api_session, tmp_path, monkeypatch, FakeAssistant([_citation()])) as c:
        r = c.post("/assistant/ask", json={"query": "why?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["has_citations"] is True
    assert body["answer"] == "answer [1]"
    assert len(body["citations"]) == 1


@pytest.mark.integration
def test_ask_fail_closed(api_session, tmp_path, monkeypatch) -> None:
    with _client(api_session, tmp_path, monkeypatch, FakeAssistant([])) as c:
        r = c.post("/assistant/ask", json={"query": "obscure"})
    assert r.status_code == 200
    body = r.json()
    assert body["has_citations"] is False
    assert body["answer"] is None
    assert body["citations"] == []


@pytest.mark.integration
def test_stream_emits_tokens_then_citations(api_session, tmp_path, monkeypatch) -> None:
    with _client(api_session, tmp_path, monkeypatch, FakeAssistant([_citation()])) as c:
        r = c.post("/assistant/stream", json={"query": "why?"})
    assert r.status_code == 200
    text = r.text
    assert "event: token" in text
    assert "event: citations" in text
    assert '"has_citations": true' in text
    assert text.rstrip().endswith("event: done\ndata: {}") or "event: done" in text


@pytest.mark.integration
def test_stream_fail_closed_has_no_tokens(api_session, tmp_path, monkeypatch) -> None:
    with _client(api_session, tmp_path, monkeypatch, FakeAssistant([])) as c:
        r = c.post("/assistant/stream", json={"query": "obscure"})
    assert r.status_code == 200
    text = r.text
    assert "event: token" not in text
    assert '"has_citations": false' in text
