"""Integration tests — audit log invariants for execution status changes."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_execution.dto import GoalInput, StatusUpdate, TaskInput
from eci_execution.goal_service import GoalService
from eci_execution.task_service import TaskService
from eci_storage.models.audit import AuditEvent


@pytest.mark.integration
def test_goal_status_change_produces_audit_event(db_session: Session) -> None:
    svc = GoalService(db_session)
    goal = svc.create_goal(GoalInput(title="Audited goal"))
    svc.update_status(goal.id, StatusUpdate(status="in_progress", actor="ci-bot", reason="Sprint started"))

    events = list(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.target_id == goal.id,
                AuditEvent.action == "goal.status_change",
            )
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt.actor == "ci-bot"
    assert evt.prior_state == {"status": "pending"}
    assert evt.new_state == {"status": "in_progress"}
    assert evt.reason == "Sprint started"


@pytest.mark.integration
def test_task_status_change_produces_audit_event(db_session: Session) -> None:
    svc = TaskService(db_session)
    task = svc.create_task(TaskInput(title="Audited task"))
    svc.update_status(task.id, StatusUpdate(status="completed", reason="Done"))

    events = list(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.target_id == task.id,
                AuditEvent.action == "task.status_change",
            )
        )
    )
    assert len(events) == 1
    assert events[0].prior_state == {"status": "pending"}
    assert events[0].new_state == {"status": "completed"}


@pytest.mark.integration
def test_multiple_status_changes_all_audited(db_session: Session) -> None:
    svc = GoalService(db_session)
    goal = svc.create_goal(GoalInput(title="Multi-transition goal"))
    svc.update_status(goal.id, StatusUpdate(status="in_progress"))
    svc.update_status(goal.id, StatusUpdate(status="blocked", reason="Dependency blocked"))
    svc.update_status(goal.id, StatusUpdate(status="in_progress"))

    events = list(
        db_session.scalars(
            select(AuditEvent)
            .where(AuditEvent.target_id == goal.id)
            .order_by(AuditEvent.occurred_at)
        )
    )
    assert len(events) == 3
    statuses = [(e.prior_state["status"], e.new_state["status"]) for e in events]
    assert statuses == [
        ("pending", "in_progress"),
        ("in_progress", "blocked"),
        ("blocked", "in_progress"),
    ]


@pytest.mark.integration
def test_audit_actor_defaults_to_system(db_session: Session) -> None:
    svc = TaskService(db_session)
    task = svc.create_task(TaskInput(title="System task"))
    svc.update_status(task.id, StatusUpdate(status="in_progress"))

    events = list(
        db_session.scalars(
            select(AuditEvent).where(AuditEvent.target_id == task.id)
        )
    )
    assert events[0].actor == "system"
