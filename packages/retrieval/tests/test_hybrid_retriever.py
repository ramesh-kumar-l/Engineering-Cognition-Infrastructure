"""Integration tests for HybridRetriever — requires real Postgres."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_retrieval.dto import RetrievalRequest
from eci_retrieval.embedding_service import EmbeddingService
from eci_retrieval.hybrid_retriever import HybridRetriever


@pytest.mark.integration
def test_retrieve_empty_index_returns_no_citations(
    db_session: Session,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    """With no embeddings in DB, retrieval returns an empty-citations result (not an error)."""
    retriever = HybridRetriever(db_session, stub_embedding_provider)
    result = retriever.retrieve(RetrievalRequest(query="knowledge management"))
    assert result.has_citations is False
    assert result.citations == []
    assert result.retrieval_stages["fts"] == 0
    assert result.retrieval_stages["vector"] == 0


@pytest.mark.integration
def test_retrieve_finds_embedded_document(
    db_session: Session,
    sample_document_id: uuid.UUID,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    # First embed the document so retrieval can find it
    embed_svc = EmbeddingService(db_session, stub_embedding_provider)
    embed_svc.embed_document(sample_document_id)

    retriever = HybridRetriever(db_session, stub_embedding_provider)
    result = retriever.retrieve(
        RetrievalRequest(query="knowledge retrieval", top_k=5)
    )
    # Vector stage should return something since embeddings exist
    assert result.retrieval_stages["vector"] >= 1
    assert result.has_citations is True
    assert all(c.source_id is not None for c in result.citations)


@pytest.mark.integration
def test_retrieve_citations_have_title_and_uri(
    db_session: Session,
    sample_document_id: uuid.UUID,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    embed_svc = EmbeddingService(db_session, stub_embedding_provider)
    embed_svc.embed_document(sample_document_id)

    retriever = HybridRetriever(db_session, stub_embedding_provider)
    result = retriever.retrieve(RetrievalRequest(query="engineering memory", top_k=3))
    assert result.has_citations
    for citation in result.citations:
        assert citation.source_uri is not None
        assert citation.chunk_index >= 0
