"""Document ingest endpoint."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from eci_identity.dto import RequestContext
from eci_ingest import (
    DocumentIngestRequest,
    DocumentIngestResult,
    DocumentIngestService,
    DocumentListItem,
    DocumentRead,
    ParseError,
    SourceReadService,
    SourceTooLarge,
    UnsupportedSource,
)
from eci_observability import request_counter
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from eci_api.auth import get_request_context
from eci_api.dependencies import get_document_service, get_source_read_service

router = APIRouter(prefix="/documents", tags=["ingest"])


@router.post(
    "",
    response_model=DocumentIngestResult,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_document(
    file: Annotated[UploadFile, File(...)],
    kind: Annotated[str, Form(...)],
    source: Annotated[str, Form(...)],
    title: Annotated[str | None, Form()] = None,
    author: Annotated[str | None, Form()] = None,
    tags: Annotated[str, Form()] = "",
    captured_at: Annotated[datetime | None, Form()] = None,
    ingested_by: Annotated[str, Form()] = "system",
    service: DocumentIngestService = Depends(get_document_service),
    ctx: RequestContext = Depends(get_request_context),
) -> DocumentIngestResult:
    raw = await file.read()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    try:
        req = DocumentIngestRequest(
            kind=kind,  # type: ignore[arg-type] — validated by Pydantic
            source=source,
            title=title,
            author=author,
            tags=tag_list,
            captured_at=captured_at,
            ingested_by=ingested_by,
        )
        result = service.ingest(req, raw, tenant_id=ctx.tenant_id)
    except UnsupportedSource as exc:
        request_counter.labels(route="/documents", method="POST", outcome="unsupported").inc()
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, str(exc)) from exc
    except SourceTooLarge as exc:
        request_counter.labels(route="/documents", method="POST", outcome="too_large").inc()
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc
    except ParseError as exc:
        request_counter.labels(route="/documents", method="POST", outcome="parse_error").inc()
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

    outcome = "dedup" if result.deduplicated else "created"
    request_counter.labels(route="/documents", method="POST", outcome=outcome).inc()
    return result


@router.get("", response_model=list[DocumentListItem])
def list_documents(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    reader: SourceReadService = Depends(get_source_read_service),
    ctx: RequestContext = Depends(get_request_context),
) -> list[DocumentListItem]:
    return reader.list_documents(ctx.tenant_id, limit=limit, offset=offset)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: uuid.UUID,
    reader: SourceReadService = Depends(get_source_read_service),
    ctx: RequestContext = Depends(get_request_context),
) -> DocumentRead:
    doc = reader.get_document(document_id, ctx.tenant_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return doc
