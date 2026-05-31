"""Shared fixtures for reflection integration tests."""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_ECI_TEST_DB_URL = os.getenv("ECI_TEST_DB_URL")


@pytest.fixture(scope="session")
def db_engine():  # type: ignore[no-untyped-def]
    if not _ECI_TEST_DB_URL:
        pytest.skip("ECI_TEST_DB_URL not set — skipping integration tests")
    return create_engine(_ECI_TEST_DB_URL)


@pytest.fixture
def db_session(db_engine):  # type: ignore[no-untyped-def]
    conn = db_engine.connect()
    txn = conn.begin()
    factory = sessionmaker(bind=conn)
    session: Session = factory()
    yield session
    session.close()
    txn.rollback()
    conn.close()


@pytest.fixture
def stub_llm_provider():  # type: ignore[no-untyped-def]
    """Minimal LLMProvider stub that returns a valid JSON lesson array."""
    from eci_llm.protocol import LLMProvider, LLMRequest, LLMResponse

    class _StubProvider:
        model_name = "stub"

        def complete(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(
                content='[{"claim": "Invest early in test automation", '
                '"scope": "project", "confidence": "high", "evidence_indices": [0]}]',
                model=self.model_name,
                prompt_tokens=10,
                completion_tokens=30,
            )

    return _StubProvider()


@pytest.fixture
def empty_llm_provider():  # type: ignore[no-untyped-def]
    """Stub provider that returns an empty lesson array (no patterns found)."""
    from eci_llm.protocol import LLMProvider, LLMRequest, LLMResponse

    class _EmptyProvider:
        model_name = "stub-empty"

        def complete(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(content="[]", model=self.model_name, prompt_tokens=5, completion_tokens=2)

    return _EmptyProvider()


@pytest.fixture
def sample_goal_id(db_session: Session) -> uuid.UUID:
    from eci_storage.models.goal import Goal

    goal = Goal(title="Build CI pipeline", description="Automate everything", status="completed")
    db_session.add(goal)
    db_session.flush()
    return goal.id  # type: ignore[return-value]


@pytest.fixture
def sample_task_id(db_session: Session, sample_goal_id: uuid.UUID) -> uuid.UUID:
    from eci_storage.models.task import Task

    task = Task(title="Write unit tests", goal_id=sample_goal_id, status="completed")
    db_session.add(task)
    db_session.flush()
    return task.id  # type: ignore[return-value]
