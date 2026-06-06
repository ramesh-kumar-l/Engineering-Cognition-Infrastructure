"""Note ingest endpoint."""

from __future__ import annotations

import uuid

from eci_identity.dto import RequestContext
from eci_ingest import (
    NoteIngestRequest,
    NoteIngestResult,
    NoteIngestService,
    NoteRead,
    SourceReadService,
    SourceTooLarge,
)
from eci_observability import request_counter
from fastapi import APIRouter, Depends, HTTPException, status

from eci_api.auth import get_request_context
from eci_api.dependencies import get_note_service, get_source_read_service

router = APIRouter(prefix="/notes", tags=["ingest"])


@router.post(
    "",
    response_model=NoteIngestResult,
    status_code=status.HTTP_201_CREATED,
)
def ingest_note(
    body: NoteIngestRequest,
    service: NoteIngestService = Depends(get_note_service),
    ctx: RequestContext = Depends(get_request_context),
) -> NoteIngestResult:
    try:
        result = service.ingest(body, tenant_id=ctx.tenant_id)
    except SourceTooLarge as exc:
        request_counter.labels(route="/notes", method="POST", outcome="too_large").inc()
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc

    outcome = "dedup" if result.deduplicated else "created"
    request_counter.labels(route="/notes", method="POST", outcome=outcome).inc()
    return result


@router.get("/{note_id}", response_model=NoteRead)
def get_note(
    note_id: uuid.UUID,
    reader: SourceReadService = Depends(get_source_read_service),
    ctx: RequestContext = Depends(get_request_context),
) -> NoteRead:
    note = reader.get_note(note_id, ctx.tenant_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return note
