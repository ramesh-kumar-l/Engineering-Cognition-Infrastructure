"""Retrospectives router.

Endpoints:
  POST /retrospectives         → create and run a reflection cycle (201)
  GET  /retrospectives         → list all retrospectives
  GET  /retrospectives/{id}    → get one retrospective
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from eci_api.dependencies import get_retrospective_service
from eci_reflection.dto import RetrospectiveInput, RetrospectiveOut
from eci_reflection.errors import InvalidCadenceError, RetrospectiveNotFoundError
from eci_reflection.retrospective_service import RetrospectiveService

router = APIRouter(prefix="/retrospectives", tags=["retrospectives"])


class CreateRetrospectiveRequest(BaseModel):
    cadence: str = Field(..., pattern="^(weekly|monthly|milestone)$")
    scope_type: str | None = Field(default=None, pattern="^(roadmap|goal|global)$")
    scope_id: uuid.UUID | None = None
    notes: str | None = None


class RetrospectiveResponse(BaseModel):
    id: uuid.UUID
    cadence: str
    scope_type: str | None
    scope_id: uuid.UUID | None
    status: str
    lesson_count: int
    notes: str | None


def _to_resp(out: RetrospectiveOut) -> RetrospectiveResponse:
    return RetrospectiveResponse(
        id=out.id,
        cadence=out.cadence,
        scope_type=out.scope_type,
        scope_id=out.scope_id,
        status=out.status,
        lesson_count=out.lesson_count,
        notes=out.notes,
    )


@router.post("", response_model=RetrospectiveResponse, status_code=status.HTTP_201_CREATED)
def create_retrospective(
    body: CreateRetrospectiveRequest,
    svc: RetrospectiveService = Depends(get_retrospective_service),
) -> RetrospectiveResponse:
    try:
        out = svc.create_and_run(
            RetrospectiveInput(
                cadence=body.cadence,
                scope_type=body.scope_type,
                scope_id=body.scope_id,
                notes=body.notes,
            )
        )
        return _to_resp(out)
    except InvalidCadenceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("", response_model=list[RetrospectiveResponse])
def list_retrospectives(
    svc: RetrospectiveService = Depends(get_retrospective_service),
) -> list[RetrospectiveResponse]:
    return [_to_resp(r) for r in svc.list_retrospectives()]


@router.get("/{retro_id}", response_model=RetrospectiveResponse)
def get_retrospective(
    retro_id: uuid.UUID,
    svc: RetrospectiveService = Depends(get_retrospective_service),
) -> RetrospectiveResponse:
    try:
        return _to_resp(svc.get_retrospective(retro_id))
    except RetrospectiveNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
