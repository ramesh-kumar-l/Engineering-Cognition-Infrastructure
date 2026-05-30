"""Shared fixtures for storage + ingest integration tests.

Integration tests require a real Postgres reachable at ECI_TEST_DB_URL.
Without the env var, integration tests are skipped (CI provides it).
"""

from __future__ import annotations

import os
from typing import Iterator

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from eci_storage.models import Base


def _test_db_url() -> str | None:
    return os.environ.get("ECI_TEST_DB_URL")


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = _test_db_url()
    if not url:
        pytest.skip("ECI_TEST_DB_URL not set; integration tests skipped")
    eng = create_engine(url, future=True, pool_pre_ping=True)
    # Ensure schema exists. CI runs alembic; locally we fall back to create_all.
    with eng.begin() as conn:
        result = conn.execute(
            text("SELECT to_regclass('public.raw_blobs')")
        ).scalar()
        if result is None:
            Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def db_session(engine: Engine) -> Iterator[Session]:
    """Transactional fixture: every test runs inside a rollback'd transaction."""
    connection = engine.connect()
    transaction = connection.begin()
    factory = sessionmaker(bind=connection, expire_on_commit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
