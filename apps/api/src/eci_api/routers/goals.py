"""Goals router — Goal CRUD, status updates, and citation retrieval.

Endpoints:
  POST /goals                   → create goal (with optional citations)
  GET  /goals                   → list goals (optional ?roadmap_id filter)
  GET  /goals/{id}              → get by ID
  PATCH /goals/{id}/status      → update status
  GET  /goals/{id}/why          → source citations ("why does this goal exist?")
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from eci_api.dependencies import get_goal_service
from eci_execution.dto import CitationInput, CitationOut, GoalInput, GoalOut, StatusUpdate
from eci_execution.errors import GoalNotFoundError, InvalidStatusError
from eci_execution.goal_service import GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


class CitationPayload(BaseModel):
    source_type: str
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    title: str | None = None
    source_uri: str | None = None


class CreateGoalRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    description: str | None = None
    roadmap_id: uuid.UUID | None = None
    source_memory_id: uuid.UUID | None = None
    citations: list[CitationPayload] = Field(default_factory=list)


class GoalResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: str
    roadmap_id: uuid.UUID | None
    source_memory_id: uuid.UUID | None


class StatusUpdateRequest(BaseModel):
    status: str = Field(..., min_length=1)
    reason: str | None = None
    actor: str = "system"


class CitationResponse(BaseModel):
    target_type: str
    target_id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    title: str | None
    source_uri: str | None


def _to_goal_resp(out: GoalOut) -> GoalResponse:
    return GoalResponse(
        id=out.id,
        title=out.title,
        description=out.description,
        status=out.status,
        roadmap_id=out.roadmap_id,
        source_memory_id=out.source_memory_id,
    )


def _to_citation_resp(c: CitationOut) -> CitationResponse:
    return CitationResponse(
        target_type=c.target_type,
        target_id=c.target_id,
        source_type=c.source_type,
        source_id=c.source_id,
        chunk_index=c.chunk_index,
        content=c.content,
        score=c.score,
        title=c.title,
        source_uri=c.source_uri,
    )


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    body: CreateGoalRequest,
    svc: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    inp = GoalInput(
        title=body.title,
        description=body.description,
        roadmap_id=body.roadmap_id,
        source_memory_id=body.source_memory_id,
        citations=[
            CitationInput(
                source_type=c.source_type,
                source_id=c.source_id,
                chunk_index=c.chunk_index,
                content=c.content,
                score=c.score,
                title=c.title,
                source_uri=c.source_uri,
            )
            for c in body.citations
        ],
    )
    return _to_goal_resp(svc.create_goal(inp))


@router.get("", response_model=list[GoalResponse])
def list_goals(
    roadmap_id: uuid.UUID | None = Query(default=None),
    svc: GoalService = Depends(get_goal_service),
) -> list[GoalResponse]:
    return [_to_goal_resp(g) for g in svc.list_goals(roadmap_id=roadmap_id)]


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: uuid.UUID,
    svc: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    try:
        return _to_goal_resp(svc.get_goal(goal_id))
    except GoalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{goal_id}/status", response_model=GoalResponse)
def update_goal_status(
    goal_id: uuid.UUID,
    body: StatusUpdateRequest,
    svc: GoalService = Depends(get_goal_service),
) -> GoalResponse:
    try:
        return _to_goal_resp(
            svc.update_status(
                goal_id,
                StatusUpdate(status=body.status, reason=body.reason, actor=body.actor),
            )
        )
    except GoalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidStatusError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/{goal_id}/why", response_model=list[CitationResponse])
def get_goal_citations(
    goal_id: uuid.UUID,
    svc: GoalService = Depends(get_goal_service),
) -> list[CitationResponse]:
    """Return source citations justifying why this goal exists."""
    try:
        return [_to_citation_resp(c) for c in svc.get_citations(goal_id)]
    except GoalNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
