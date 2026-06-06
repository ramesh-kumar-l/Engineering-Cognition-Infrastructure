"""Assistant router — grounded, citation-backed answers over the corpus.

POST /assistant/ask     → JSON answer (fail-closed when no citations).
POST /assistant/stream  → text/event-stream: `token` frames, then a `citations` frame.

Fail-closed (AP-2): when retrieval yields no citations, the LLM is never invoked.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator

from eci_identity.dto import RequestContext
from eci_retrieval.assistant_service import AssistantService
from eci_retrieval.dto import Citation
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from eci_api.auth import get_request_context
from eci_api.dependencies import get_assistant_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=50)


class CitationOut(BaseModel):
    source_type: str
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    title: str | None
    source_uri: str | None


class AskResponse(BaseModel):
    query: str
    answer: str | None
    has_citations: bool
    citations: list[CitationOut]


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


@router.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    svc: AssistantService = Depends(get_assistant_service),
    ctx: RequestContext = Depends(get_request_context),
) -> AskResponse:
    result = svc.ask(body.query, body.top_k, ctx.tenant_id)
    return AskResponse(
        query=result.query,
        answer=result.answer,
        has_citations=result.has_citations,
        citations=[_citation_out(c) for c in result.citations],
    )


def _sse(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/stream")
def stream(
    body: AskRequest,
    svc: AssistantService = Depends(get_assistant_service),
    ctx: RequestContext = Depends(get_request_context),
) -> StreamingResponse:
    result = svc.retrieve(body.query, body.top_k, ctx.tenant_id)

    def gen() -> Iterator[str]:
        if not result.has_citations:
            # Fail-closed: no evidence → no generation.
            yield _sse("citations", {"has_citations": False, "citations": []})
            yield _sse("done", {})
            return
        for token in svc.stream_answer(body.query, result.citations):
            yield _sse("token", {"text": token})
        yield _sse(
            "citations",
            {
                "has_citations": True,
                "citations": [_citation_out(c).model_dump(mode="json") for c in result.citations],
            },
        )
        yield _sse("done", {})

    return StreamingResponse(gen(), media_type="text/event-stream")
