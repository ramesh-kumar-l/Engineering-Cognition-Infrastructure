"""RoadmapService — CRUD for Roadmap records."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_observability import get_logger
from eci_execution.dto import RoadmapInput, RoadmapOut
from eci_execution.errors import RoadmapNotFoundError
from eci_storage.models.roadmap import Roadmap

_log = get_logger("eci_execution.roadmap_service")


def _to_out(r: Roadmap) -> RoadmapOut:
    return RoadmapOut(
        id=r.id,
        title=r.title,
        description=r.description,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


class RoadmapService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_roadmap(self, inp: RoadmapInput) -> RoadmapOut:
        roadmap = Roadmap(title=inp.title, description=inp.description)
        self._session.add(roadmap)
        self._session.flush()
        _log.info("roadmap.created", roadmap_id=str(roadmap.id))
        return _to_out(roadmap)

    def get_roadmap(self, roadmap_id: uuid.UUID) -> RoadmapOut:
        roadmap = self._session.get(Roadmap, roadmap_id)
        if roadmap is None:
            raise RoadmapNotFoundError(f"Roadmap {roadmap_id} not found")
        return _to_out(roadmap)

    def list_roadmaps(self, tenant_id: uuid.UUID | None = None) -> list[RoadmapOut]:
        stmt = select(Roadmap).order_by(Roadmap.created_at)
        if tenant_id is not None:
            stmt = stmt.where(Roadmap.tenant_id == tenant_id)
        rows = self._session.scalars(stmt)
        return [_to_out(r) for r in rows]
