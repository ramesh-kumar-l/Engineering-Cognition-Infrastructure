"""Compression router — triggers and retrieves compression artifacts.

Endpoints:
  POST /compress/documents/{document_id}  → run compression pipeline
  POST /compress/notes/{note_id}          → run compression pipeline
  GET  /compress/documents/{document_id}/summaries    → list summaries
  GET  /compress/documents/{document_id}/mental-model → get mental model
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_api.dependencies import get_compression_service, get_db
from eci_compression.compression_service import CompressionService
from eci_compression.dto import CompressionRequest, SourceType
from eci_compression.errors import SourceNotFound
from eci_storage.models.mental_model import MentalModel
from eci_storage.models.summary import Summary

router = APIRouter(prefix="/compress", tags=["compression"])


class CompressResponse(BaseModel):
    source_id: uuid.UUID
    source_type: str
    summaries_created: int
    has_mental_model: bool
    has_playbook: bool


class SummaryOut(BaseModel):
    id: uuid.UUID
    level: str
    word_count: int
    model_used: str
    content: str = Field(..., description="Full summary text")


class MentalModelOut(BaseModel):
    id: uuid.UUID
    claims: list[str]
    entities: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    has_playbook: bool
    model_used: str


@router.post("/documents/{document_id}", response_model=CompressResponse)
def compress_document(
    document_id: uuid.UUID,
    service: CompressionService = Depends(get_compression_service),
) -> CompressResponse:
    req = CompressionRequest(source_id=document_id, source_type=SourceType.DOCUMENT)
    try:
        result = service.compress(req)
    except SourceNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return CompressResponse(
        source_id=result.source_id,
        source_type=result.source_type.value,
        summaries_created=len(result.summaries),
        has_mental_model=result.mental_model is not None,
        has_playbook=(
            result.playbook is not None and result.playbook.title is not None
        ),
    )


@router.post("/notes/{note_id}", response_model=CompressResponse)
def compress_note(
    note_id: uuid.UUID,
    service: CompressionService = Depends(get_compression_service),
) -> CompressResponse:
    req = CompressionRequest(source_id=note_id, source_type=SourceType.NOTE)
    try:
        result = service.compress(req)
    except SourceNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return CompressResponse(
        source_id=result.source_id,
        source_type=result.source_type.value,
        summaries_created=len(result.summaries),
        has_mental_model=result.mental_model is not None,
        has_playbook=(
            result.playbook is not None and result.playbook.title is not None
        ),
    )


@router.get("/documents/{document_id}/summaries", response_model=list[SummaryOut])
def get_document_summaries(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[SummaryOut]:
    rows = db.scalars(
        select(Summary)
        .where(Summary.document_id == document_id)
        .order_by(Summary.created_at)
    ).all()
    return [
        SummaryOut(
            id=r.id,
            level=r.level,
            word_count=r.word_count,
            model_used=r.model_used,
            content=r.content,
        )
        for r in rows
    ]


@router.get("/documents/{document_id}/mental-model", response_model=MentalModelOut)
def get_document_mental_model(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> MentalModelOut:
    row = db.scalar(
        select(MentalModel)
        .where(MentalModel.document_id == document_id)
        .order_by(MentalModel.created_at.desc())
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Mental model not found")
    return MentalModelOut(
        id=row.id,
        claims=row.claims,
        entities=row.entities,
        relationships=row.relationships,
        has_playbook=bool(row.playbook),
        model_used=row.model_used,
    )
