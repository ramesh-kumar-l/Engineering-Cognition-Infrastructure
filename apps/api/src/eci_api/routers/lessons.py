"""Lessons router.

Endpoints:
  POST /lessons                       → manually create a lesson (201)
  GET  /lessons                       → list lessons (filter: ?retrospective_id, ?status)
  GET  /lessons/{id}                  → get lesson with evidence
  POST /lessons/{id}/supersede        → supersede with a new lesson (201)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from eci_api.dependencies import get_lesson_service
from eci_reflection.dto import EvidenceInput, LessonInput, LessonOut
from eci_reflection.errors import (
    InvalidConfidenceError,
    LessonNotFoundError,
    SupersessionError,
)
from eci_reflection.lesson_service import LessonService

router = APIRouter(prefix="/lessons", tags=["lessons"])


class EvidencePayload(BaseModel):
    source_type: str
    source_id: uuid.UUID
    summary: str


class CreateLessonRequest(BaseModel):
    claim: str = Field(..., min_length=1)
    scope: str = "global"
    confidence: str = "medium"
    retrospective_id: uuid.UUID | None = None
    evidence: list[EvidencePayload] = Field(default_factory=list)


class SupersedeRequest(BaseModel):
    claim: str = Field(..., min_length=1)
    scope: str = "global"
    confidence: str = "medium"
    evidence: list[EvidencePayload] = Field(default_factory=list)
    actor: str = "system"


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    summary: str


class LessonResponse(BaseModel):
    id: uuid.UUID
    retrospective_id: uuid.UUID | None
    claim: str
    scope: str
    confidence: str
    status: str
    supersedes_id: uuid.UUID | None
    evidence: list[EvidenceResponse]


def _to_resp(out: LessonOut) -> LessonResponse:
    return LessonResponse(
        id=out.id,
        retrospective_id=out.retrospective_id,
        claim=out.claim,
        scope=out.scope,
        confidence=out.confidence,
        status=out.status,
        supersedes_id=out.supersedes_id,
        evidence=[
            EvidenceResponse(
                id=e.id, source_type=e.source_type, source_id=e.source_id, summary=e.summary
            )
            for e in out.evidence
        ],
    )


@router.post("", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    body: CreateLessonRequest,
    svc: LessonService = Depends(get_lesson_service),
) -> LessonResponse:
    try:
        out = svc.create_lesson(
            LessonInput(
                claim=body.claim,
                scope=body.scope,
                confidence=body.confidence,
                retrospective_id=body.retrospective_id,
                evidence=[
                    EvidenceInput(
                        source_type=e.source_type, source_id=e.source_id, summary=e.summary
                    )
                    for e in body.evidence
                ],
            )
        )
        return _to_resp(out)
    except InvalidConfidenceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("", response_model=list[LessonResponse])
def list_lessons(
    retrospective_id: uuid.UUID | None = Query(default=None),
    filter_status: str | None = Query(default=None, alias="status"),
    svc: LessonService = Depends(get_lesson_service),
) -> list[LessonResponse]:
    return [_to_resp(l) for l in svc.list_lessons(retrospective_id=retrospective_id, status=filter_status)]


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: uuid.UUID,
    svc: LessonService = Depends(get_lesson_service),
) -> LessonResponse:
    try:
        return _to_resp(svc.get_lesson(lesson_id))
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{lesson_id}/supersede", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def supersede_lesson(
    lesson_id: uuid.UUID,
    body: SupersedeRequest,
    svc: LessonService = Depends(get_lesson_service),
) -> LessonResponse:
    try:
        out = svc.supersede(
            lesson_id,
            LessonInput(
                claim=body.claim,
                scope=body.scope,
                confidence=body.confidence,
                evidence=[
                    EvidenceInput(
                        source_type=e.source_type, source_id=e.source_id, summary=e.summary
                    )
                    for e in body.evidence
                ],
            ),
            actor=body.actor,
        )
        return _to_resp(out)
    except LessonNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SupersessionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except InvalidConfidenceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
