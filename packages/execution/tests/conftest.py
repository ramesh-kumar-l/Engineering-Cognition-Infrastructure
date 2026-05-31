"""Shared fixtures for execution integration tests."""

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
def sample_memory_entry_id(db_session: Session) -> uuid.UUID:
    """Insert a minimal MemoryEntry for FK linkage tests."""
    from eci_storage.models.memory_entry import MemoryEntry

    entry = MemoryEntry(
        title="Test memory entry for execution tests",
        body="This memory entry motivates the goals and tasks created in tests.",
        tags=[],
        source_type=None,
        source_id=None,
        version=1,
        is_current=True,
    )
    db_session.add(entry)
    db_session.flush()
    return entry.id  # type: ignore[return-value]
