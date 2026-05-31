"""TaskService — CRUD, dependency edges, and citation retrieval for tasks."""

from __future__ import annotations

import uuid
from collections import deque

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_observability import get_logger
from eci_execution.audit_service import record_status_change
from eci_execution.citation_helpers import store_citations, to_citation_out
from eci_execution.dto import CitationOut, StatusUpdate, TaskInput, TaskOut, VALID_STATUSES
from eci_execution.errors import DependencyCycleError, InvalidStatusError, TaskNotFoundError
from eci_storage.models.base import utcnow
from eci_storage.models.execution_citation import ExecutionCitation
from eci_storage.models.task import Task
from eci_storage.models.task_dependency import TaskDependency

_log = get_logger("eci_execution.task_service")


def _to_task_out(t: Task) -> TaskOut:
    return TaskOut(
        id=t.id,
        title=t.title,
        description=t.description,
        status=t.status,
        goal_id=t.goal_id,
        position=t.position,
        source_memory_id=t.source_memory_id,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


def _can_reach(session: Session, from_id: uuid.UUID, to_id: uuid.UUID) -> bool:
    """BFS reachability: True if to_id is reachable from from_id via downstream edges."""
    visited: set[uuid.UUID] = set()
    queue: deque[uuid.UUID] = deque([from_id])
    while queue:
        current = queue.popleft()
        if current == to_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        children = session.scalars(
            select(TaskDependency.downstream_id).where(TaskDependency.upstream_id == current)
        )
        queue.extend(children)
    return False


class TaskService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_task(self, inp: TaskInput) -> TaskOut:
        task = Task(
            title=inp.title,
            description=inp.description,
            status="pending",
            goal_id=inp.goal_id,
            position=inp.position,
            source_memory_id=inp.source_memory_id,
        )
        self._session.add(task)
        self._session.flush()

        store_citations(self._session, "task", task.id, inp.citations)
        self._session.flush()

        _log.info("task.created", task_id=str(task.id), citations=len(inp.citations))
        return _to_task_out(task)

    def get_task(self, task_id: uuid.UUID) -> TaskOut:
        task = self._session.get(Task, task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return _to_task_out(task)

    def list_tasks(
        self,
        goal_id: uuid.UUID | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> list[TaskOut]:
        stmt = select(Task).order_by(Task.position, Task.created_at)
        if goal_id is not None:
            stmt = stmt.where(Task.goal_id == goal_id)
        if tenant_id is not None:
            stmt = stmt.where(Task.tenant_id == tenant_id)
        return [_to_task_out(t) for t in self._session.scalars(stmt)]

    def update_status(self, task_id: uuid.UUID, update: StatusUpdate) -> TaskOut:
        if update.status not in VALID_STATUSES:
            raise InvalidStatusError(f"Unknown status: {update.status!r}")
        task = self._session.get(Task, task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")

        prior = task.status
        task.status = update.status
        task.updated_at = utcnow()

        record_status_change(
            self._session,
            actor=update.actor,
            target_type="task",
            target_id=task_id,
            prior_status=prior,
            new_status=update.status,
            reason=update.reason,
        )
        self._session.flush()
        _log.info("task.status_changed", task_id=str(task_id), from_=prior, to=update.status)
        return _to_task_out(task)

    def add_dependency(self, upstream_id: uuid.UUID, downstream_id: uuid.UUID) -> None:
        """Add prerequisite edge: upstream must complete before downstream.

        Raises DependencyCycleError if the edge would create a cycle.
        """
        if upstream_id == downstream_id:
            raise DependencyCycleError("A task cannot depend on itself")
        if self._session.get(Task, upstream_id) is None:
            raise TaskNotFoundError(f"Task {upstream_id} not found")
        if self._session.get(Task, downstream_id) is None:
            raise TaskNotFoundError(f"Task {downstream_id} not found")

        if _can_reach(self._session, downstream_id, upstream_id):
            raise DependencyCycleError(
                f"Adding {upstream_id}→{downstream_id} would create a dependency cycle"
            )

        if self._session.get(TaskDependency, (upstream_id, downstream_id)) is None:
            self._session.add(
                TaskDependency(upstream_id=upstream_id, downstream_id=downstream_id)
            )
            self._session.flush()
            _log.info(
                "task.dependency_added",
                upstream=str(upstream_id),
                downstream=str(downstream_id),
            )

    def get_citations(self, task_id: uuid.UUID) -> list[CitationOut]:
        """Return stored citations — the answer to 'why does this task exist?'"""
        if self._session.get(Task, task_id) is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        rows = self._session.scalars(
            select(ExecutionCitation)
            .where(
                ExecutionCitation.target_type == "task",
                ExecutionCitation.target_id == task_id,
            )
            .order_by(ExecutionCitation.score.desc())
        )
        return [to_citation_out(r) for r in rows]
