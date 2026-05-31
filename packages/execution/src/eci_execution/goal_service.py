"""GoalService — create, read, update, and explain goals."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_observability import get_logger
from eci_execution.audit_service import record_status_change
from eci_execution.citation_helpers import store_citations, to_citation_out
from eci_execution.dto import CitationOut, GoalInput, GoalOut, StatusUpdate, VALID_STATUSES
from eci_execution.errors import GoalNotFoundError, InvalidStatusError
from eci_storage.models.base import utcnow
from eci_storage.models.execution_citation import ExecutionCitation
from eci_storage.models.goal import Goal

_log = get_logger("eci_execution.goal_service")


def _to_goal_out(g: Goal) -> GoalOut:
    return GoalOut(
        id=g.id,
        title=g.title,
        description=g.description,
        status=g.status,
        roadmap_id=g.roadmap_id,
        source_memory_id=g.source_memory_id,
        created_at=g.created_at,
        updated_at=g.updated_at,
    )


class GoalService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_goal(self, inp: GoalInput) -> GoalOut:
        goal = Goal(
            title=inp.title,
            description=inp.description,
            status="pending",
            roadmap_id=inp.roadmap_id,
            source_memory_id=inp.source_memory_id,
        )
        self._session.add(goal)
        self._session.flush()

        store_citations(self._session, "goal", goal.id, inp.citations)
        self._session.flush()

        _log.info("goal.created", goal_id=str(goal.id), citations=len(inp.citations))
        return _to_goal_out(goal)

    def get_goal(self, goal_id: uuid.UUID) -> GoalOut:
        goal = self._session.get(Goal, goal_id)
        if goal is None:
            raise GoalNotFoundError(f"Goal {goal_id} not found")
        return _to_goal_out(goal)

    def list_goals(self, roadmap_id: uuid.UUID | None = None) -> list[GoalOut]:
        stmt = select(Goal).order_by(Goal.created_at)
        if roadmap_id is not None:
            stmt = stmt.where(Goal.roadmap_id == roadmap_id)
        return [_to_goal_out(g) for g in self._session.scalars(stmt)]

    def update_status(self, goal_id: uuid.UUID, update: StatusUpdate) -> GoalOut:
        if update.status not in VALID_STATUSES:
            raise InvalidStatusError(f"Unknown status: {update.status!r}")
        goal = self._session.get(Goal, goal_id)
        if goal is None:
            raise GoalNotFoundError(f"Goal {goal_id} not found")

        prior = goal.status
        goal.status = update.status
        goal.updated_at = utcnow()

        record_status_change(
            self._session,
            actor=update.actor,
            target_type="goal",
            target_id=goal_id,
            prior_status=prior,
            new_status=update.status,
            reason=update.reason,
        )
        self._session.flush()
        _log.info("goal.status_changed", goal_id=str(goal_id), from_=prior, to=update.status)
        return _to_goal_out(goal)

    def get_citations(self, goal_id: uuid.UUID) -> list[CitationOut]:
        """Return stored citations — the answer to 'why does this goal exist?'"""
        if self._session.get(Goal, goal_id) is None:
            raise GoalNotFoundError(f"Goal {goal_id} not found")
        rows = self._session.scalars(
            select(ExecutionCitation)
            .where(
                ExecutionCitation.target_type == "goal",
                ExecutionCitation.target_id == goal_id,
            )
            .order_by(ExecutionCitation.score.desc())
        )
        return [to_citation_out(r) for r in rows]
