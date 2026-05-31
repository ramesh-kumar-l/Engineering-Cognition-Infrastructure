"""Retrieval router — embed sources and search with citations.

Endpoints:
  POST /retrieval/embed/documents/{document_id}  → trigger embedding pipeline
  POST /retrieval/embed/notes/{note_id}          → trigger embedding pipeline
  POST /retrieval/search                         → hybrid search, returns citations
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from eci_api.auth import get_request_context
from eci_api.dependencies import get_embedding_service, get_hybrid_retriever
from eci_identity.dto import RequestContext
from eci_retrieval.dto import Citation, RetrievalRequest
from eci_retrieval.embedding_service import EmbeddingService
from eci_retrieval.errors import EmbeddingError, SourceNotFoundError
from eci_retrieval.hybrid_retriever import HybridRetriever

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


class EmbedResponse(BaseModel):
    source_id: uuid.UUID
    source_type: str
    chunks_embedded: int


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=10, ge=1, le=50)
    source_types: list[str] = Field(default=["document", "note"])


class CitationOut(BaseModel):
    source_type: str
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    title: str | None
    source_uri: str | None


class SearchResponse(BaseModel):
    query: str
    has_citations: bool
    citations: list[CitationOut]
    retrieval_stages: dict[str, int]


def _citation_out(c: Citation) -> CitationOut:
    return CitationOut(
        source_type=c.source_type,
        source_id=c.source_id,
        chunk_index=c.chunk_index,
        content=c.content,
        score=c.score,
        title=c.title,
        source_uri=c.source_uri,
    )


@router.post("/embed/documents/{document_id}", response_model=EmbedResponse)
def embed_document(
    document_id: uuid.UUID,
    svc: EmbeddingService = Depends(get_embedding_service),
) -> EmbedResponse:
    try:
        count = svc.embed_document(document_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmbeddingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc
    return EmbedResponse(
        source_id=document_id, source_type="document", chunks_embedded=count
    )


@router.post("/embed/notes/{note_id}", response_model=EmbedResponse)
def embed_note(
    note_id: uuid.UUID,
    svc: EmbeddingService = Depends(get_embedding_service),
) -> EmbedResponse:
    try:
        count = svc.embed_note(note_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmbeddingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc
    return EmbedResponse(source_id=note_id, source_type="note", chunks_embedded=count)


@router.post("/search", response_model=SearchResponse)
def search(
    body: SearchRequest,
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    ctx: RequestContext = Depends(get_request_context),
) -> SearchResponse:
    req = RetrievalRequest(
        query=body.query,
        top_k=body.top_k,
        source_types=body.source_types,
        tenant_id=ctx.tenant_id,
    )
    result = retriever.retrieve(req)
    return SearchResponse(
        query=result.query,
        has_citations=result.has_citations,
        citations=[_citation_out(c) for c in result.citations],
        retrieval_stages=result.retrieval_stages,
    )
