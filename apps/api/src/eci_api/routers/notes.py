"""Note ingest endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from eci_api.dependencies import get_note_service
from eci_ingest import (
    NoteIngestRequest,
    NoteIngestResult,
    NoteIngestService,
    SourceTooLarge,
)
from eci_observability import request_counter

router = APIRouter(prefix="/notes", tags=["ingest"])


@router.post(
    "",
    response_model=NoteIngestResult,
    status_code=status.HTTP_201_CREATED,
)
def ingest_note(
    body: NoteIngestRequest,
    service: NoteIngestService = Depends(get_note_service),
) -> NoteIngestResult:
    try:
        result = service.ingest(body)
    except SourceTooLarge as exc:
        request_counter.labels(route="/notes", method="POST", outcome="too_large").inc()
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc

    outcome = "dedup" if result.deduplicated else "created"
    request_counter.labels(route="/notes", method="POST", outcome=outcome).inc()
    return result
