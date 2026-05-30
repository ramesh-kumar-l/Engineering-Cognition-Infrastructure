"""Memory router — long-term memory entry CRUD and vector search.

Endpoints:
  POST /memory/entries              → create memory entry
  GET  /memory/entries/{entry_id}   → get by ID
  GET  /memory/entries              → list (with optional source_id filter)
  POST /memory/search               → vector similarity search
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from eci_api.dependencies import get_memory_service
from eci_retrieval.dto import MemoryEntryInput
from eci_retrieval.errors import SourceNotFoundError
from eci_retrieval.memory_service import MemoryService

router = APIRouter(prefix="/memory", tags=["memory"])


class CreateMemoryEntryRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    body: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    source_type: str | None = None
    source_id: uuid.UUID | None = None


class MemoryEntryResponse(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    tags: list[str]
    source_type: str | None
    source_id: uuid.UUID | None
    version: int
    is_current: bool


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=10, ge=1, le=50)


@router.post("/entries", response_model=MemoryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    body: CreateMemoryEntryRequest,
    svc: MemoryService = Depends(get_memory_service),
) -> MemoryEntryResponse:
    inp = MemoryEntryInput(
        title=body.title,
        body=body.body,
        tags=body.tags,
        source_type=body.source_type,
        source_id=body.source_id,
    )
    entry = svc.create_entry(inp)
    return MemoryEntryResponse(
        id=entry.id,
        title=entry.title,
        body=entry.body,
        tags=entry.tags,
        source_type=entry.source_type,
        source_id=entry.source_id,
        version=entry.version,
        is_current=entry.is_current,
    )


@router.get("/entries/{entry_id}", response_model=MemoryEntryResponse)
def get_entry(
    entry_id: uuid.UUID,
    svc: MemoryService = Depends(get_memory_service),
) -> MemoryEntryResponse:
    try:
        entry = svc.get_entry(entry_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return MemoryEntryResponse(
        id=entry.id,
        title=entry.title,
        body=entry.body,
        tags=entry.tags,
        source_type=entry.source_type,
        source_id=entry.source_id,
        version=entry.version,
        is_current=entry.is_current,
    )


@router.get("/entries", response_model=list[MemoryEntryResponse])
def list_entries(
    source_id: uuid.UUID | None = Query(default=None),
    svc: MemoryService = Depends(get_memory_service),
) -> list[MemoryEntryResponse]:
    entries = svc.list_entries(source_id=source_id)
    return [
        MemoryEntryResponse(
            id=e.id,
            title=e.title,
            body=e.body,
            tags=e.tags,
            source_type=e.source_type,
            source_id=e.source_id,
            version=e.version,
            is_current=e.is_current,
        )
        for e in entries
    ]


@router.post("/search", response_model=list[MemoryEntryResponse])
def search_entries(
    body: MemorySearchRequest,
    svc: MemoryService = Depends(get_memory_service),
) -> list[MemoryEntryResponse]:
    entries = svc.search_entries(body.query, top_k=body.top_k)
    return [
        MemoryEntryResponse(
            id=e.id,
            title=e.title,
            body=e.body,
            tags=e.tags,
            source_type=e.source_type,
            source_id=e.source_id,
            version=e.version,
            is_current=e.is_current,
        )
        for e in entries
    ]
