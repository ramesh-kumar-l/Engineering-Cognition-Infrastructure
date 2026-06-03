"""Tasks router — Task CRUD, dependency edges, status updates, and citation retrieval.

Endpoints:
  POST /tasks                        → create task
  GET  /tasks                        → list tasks (optional ?goal_id filter)
  GET  /tasks/{id}                   → get by ID
  PATCH /tasks/{id}/status           → update status
  POST /tasks/{id}/dependencies      → add upstream dependency
  GET  /tasks/{id}/why               → get source citations
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from eci_api.auth import get_request_context
from eci_api.dependencies import get_task_service
from eci_api.routers.goals import CitationPayload, CitationResponse, StatusUpdateRequest
from eci_execution.dto import CitationInput, CitationOut, StatusUpdate, TaskInput, TaskOut
from eci_execution.errors import DependencyCycleError, InvalidStatusError, TaskNotFoundError
from eci_execution.task_service import TaskService
from eci_identity.dto import RequestContext

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    goal_id: uuid.UUID | None = None
    description: str | None = None
    position: int = 0
    source_memory_id: uuid.UUID | None = None
    citations: list[CitationPayload] = Field(default_factory=list)


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: str
    goal_id: uuid.UUID | None
    position: int
    source_memory_id: uuid.UUID | None


class AddDependencyRequest(BaseModel):
    upstream_id: uuid.UUID


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


def _to_task_resp(out: TaskOut) -> TaskResponse:
    return TaskResponse(
        id=out.id,
        title=out.title,
        description=out.description,
        status=out.status,
        goal_id=out.goal_id,
        position=out.position,
        source_memory_id=out.source_memory_id,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    body: CreateTaskRequest,
    svc: TaskService = Depends(get_task_service),
    ctx: RequestContext = Depends(get_request_context),
) -> TaskResponse:
    inp = TaskInput(
        title=body.title,
        goal_id=body.goal_id,
        description=body.description,
        position=body.position,
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
    return _to_task_resp(svc.create_task(inp, tenant_id=ctx.tenant_id))


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    goal_id: uuid.UUID | None = Query(default=None),
    svc: TaskService = Depends(get_task_service),
    ctx: RequestContext = Depends(get_request_context),
) -> list[TaskResponse]:
    return [_to_task_resp(t) for t in svc.list_tasks(goal_id=goal_id, tenant_id=ctx.tenant_id)]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: uuid.UUID,
    svc: TaskService = Depends(get_task_service),
) -> TaskResponse:
    try:
        return _to_task_resp(svc.get_task(task_id))
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: uuid.UUID,
    body: StatusUpdateRequest,
    svc: TaskService = Depends(get_task_service),
) -> TaskResponse:
    try:
        return _to_task_resp(
            svc.update_status(
                task_id,
                StatusUpdate(status=body.status, reason=body.reason, actor=body.actor),
            )
        )
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidStatusError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/{task_id}/dependencies", status_code=status.HTTP_204_NO_CONTENT)
def add_dependency(
    task_id: uuid.UUID,
    body: AddDependencyRequest,
    svc: TaskService = Depends(get_task_service),
) -> None:
    """Add an upstream prerequisite: body.upstream_id must complete before task_id."""
    try:
        svc.add_dependency(upstream_id=body.upstream_id, downstream_id=task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DependencyCycleError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{task_id}/why", response_model=list[CitationResponse])
def get_task_citations(
    task_id: uuid.UUID,
    svc: TaskService = Depends(get_task_service),
) -> list[CitationResponse]:
    """Return source citations justifying why this task exists."""
    try:
        return [_to_citation_resp(c) for c in svc.get_citations(task_id)]
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
