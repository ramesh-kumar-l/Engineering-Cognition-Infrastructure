"""Tenant isolation negative tests — Tenant A cannot read Tenant B's data.

These tests verify the P7 exit criterion: a user in team A cannot read
team B's data via any service-layer list path.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_execution.dto import GoalInput, RoadmapInput, TaskInput
from eci_execution.goal_service import GoalService
from eci_execution.roadmap_service import RoadmapService
from eci_execution.task_service import TaskService
from eci_identity.dto import TenantInput, UserInput
from eci_identity.tenant_service import TenantService
from eci_identity.user_service import UserService


@pytest.mark.integration
def test_goals_isolated_by_tenant(db_session: Session) -> None:
    """Goals created in tenant A are NOT returned when listing with tenant B's ID."""
    ts = TenantService(db_session)
    slug_a, slug_b = f"iso-a-{uuid.uuid4().hex[:6]}", f"iso-b-{uuid.uuid4().hex[:6]}"
    tid_a = ts.create_tenant(TenantInput(name="A", slug=slug_a)).id
    tid_b = ts.create_tenant(TenantInput(name="B", slug=slug_b)).id

    goal_svc = GoalService(db_session)
    goal_a = goal_svc.create_goal(GoalInput(title="Alpha goal", citations=[]))
    # Manually set tenant_id on the ORM object (service layer does not set it yet;
    # isolation is enforced at query time by the tenant_id filter).
    from eci_storage.models.goal import Goal
    db_goal = db_session.get(Goal, goal_a.id)
    assert db_goal is not None
    db_goal.tenant_id = tid_a
    db_session.flush()

    # listing with tenant_b must not return tenant_a's goal
    results_b = goal_svc.list_goals(tenant_id=tid_b)
    ids_b = [g.id for g in results_b]
    assert goal_a.id not in ids_b


@pytest.mark.integration
def test_tasks_isolated_by_tenant(db_session: Session) -> None:
    """Tasks created in tenant A are NOT returned when listing with tenant B's ID."""
    ts = TenantService(db_session)
    tid_a = ts.create_tenant(TenantInput(name="A2", slug=f"ta2-{uuid.uuid4().hex[:6]}")).id
    tid_b = ts.create_tenant(TenantInput(name="B2", slug=f"tb2-{uuid.uuid4().hex[:6]}")).id

    task_svc = TaskService(db_session)
    task_a = task_svc.create_task(TaskInput(title="Task Alpha", citations=[]))
    from eci_storage.models.task import Task
    db_task = db_session.get(Task, task_a.id)
    assert db_task is not None
    db_task.tenant_id = tid_a
    db_session.flush()

    results_b = task_svc.list_tasks(tenant_id=tid_b)
    ids_b = [t.id for t in results_b]
    assert task_a.id not in ids_b


@pytest.mark.integration
def test_roadmaps_isolated_by_tenant(db_session: Session) -> None:
    """Roadmaps created in tenant A are NOT returned when listing with tenant B's ID."""
    ts = TenantService(db_session)
    tid_a = ts.create_tenant(TenantInput(name="A3", slug=f"ta3-{uuid.uuid4().hex[:6]}")).id
    tid_b = ts.create_tenant(TenantInput(name="B3", slug=f"tb3-{uuid.uuid4().hex[:6]}")).id

    rm_svc = RoadmapService(db_session)
    rm_a = rm_svc.create_roadmap(RoadmapInput(title="Alpha Roadmap"))
    from eci_storage.models.roadmap import Roadmap
    db_rm = db_session.get(Roadmap, rm_a.id)
    assert db_rm is not None
    db_rm.tenant_id = tid_a
    db_session.flush()

    results_b = rm_svc.list_roadmaps(tenant_id=tid_b)
    ids_b = [r.id for r in results_b]
    assert rm_a.id not in ids_b


@pytest.mark.integration
def test_users_isolated_by_tenant(db_session: Session) -> None:
    """Users in tenant A are not returned when listing tenant B's users."""
    ts = TenantService(db_session)
    tid_a = ts.create_tenant(TenantInput(name="A4", slug=f"ta4-{uuid.uuid4().hex[:6]}")).id
    tid_b = ts.create_tenant(TenantInput(name="B4", slug=f"tb4-{uuid.uuid4().hex[:6]}")).id

    us = UserService(db_session)
    user_a = us.create_user(UserInput(tenant_id=tid_a, email="user@ta4.io", role="member"))

    users_b = us.list_users(tid_b)
    assert user_a.id not in [u.id for u in users_b]


@pytest.mark.integration
def test_cross_tenant_user_read_is_not_filtered_at_service_level(
    db_session: Session, tenant_a: uuid.UUID, tenant_b: uuid.UUID
) -> None:
    """Direct get_user() by ID does NOT enforce tenant — that is the router's job.

    This test documents the contract: service is tenant-unaware for point
    lookups; the API router enforces the tenant_id check on GET /users/{id}.
    """
    us = UserService(db_session)
    user_a = us.create_user(UserInput(tenant_id=tenant_a, email="x@ta.io", role="member"))
    fetched = us.get_user(user_a.id)
    # Service returns the record regardless of tenant — router rejects cross-tenant reads
    assert fetched.id == user_a.id
    assert fetched.tenant_id == tenant_a
