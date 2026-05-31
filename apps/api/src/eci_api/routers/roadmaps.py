"""Roadmaps router — Roadmap CRUD.

Endpoints:
  POST /roadmaps          → create roadmap
  GET  /roadmaps          → list all roadmaps
  GET  /roadmaps/{id}     → get by ID
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from eci_api.dependencies import get_roadmap_service
from eci_execution.dto import RoadmapInput
from eci_execution.errors import RoadmapNotFoundError
from eci_execution.roadmap_service import RoadmapService

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


class CreateRoadmapRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str | None = None


class RoadmapResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None


@router.post("", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
def create_roadmap(
    body: CreateRoadmapRequest,
    svc: RoadmapService = Depends(get_roadmap_service),
) -> RoadmapResponse:
    out = svc.create_roadmap(RoadmapInput(title=body.title, description=body.description))
    return RoadmapResponse(id=out.id, title=out.title, description=out.description)


@router.get("", response_model=list[RoadmapResponse])
def list_roadmaps(svc: RoadmapService = Depends(get_roadmap_service)) -> list[RoadmapResponse]:
    return [RoadmapResponse(id=r.id, title=r.title, description=r.description) for r in svc.list_roadmaps()]


@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap(
    roadmap_id: uuid.UUID,
    svc: RoadmapService = Depends(get_roadmap_service),
) -> RoadmapResponse:
    try:
        out = svc.get_roadmap(roadmap_id)
    except RoadmapNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RoadmapResponse(id=out.id, title=out.title, description=out.description)
