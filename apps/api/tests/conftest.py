"""API integration test fixtures.

These fixtures bind the ECI storage sessionmaker to a real Postgres given by
ECI_TEST_DB_URL (skip otherwise), then override the DB dependency to use a
transactional session per test.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

import eci_storage.database as storage_db
from eci_api.dependencies import get_db
from eci_api.main import create_app
from eci_ingest.blob_store import LocalBlobStore
from eci_storage.models import Base


def _test_db_url() -> str | None:
    return os.environ.get("ECI_TEST_DB_URL")


@pytest.fixture(scope="session")
def api_engine() -> Iterator[Engine]:
    url = _test_db_url()
    if not url:
        pytest.skip("ECI_TEST_DB_URL not set; API integration tests skipped")
    eng = create_engine(url, future=True, pool_pre_ping=True)
    Base.metadata.create_all(eng)
    # Bind ECI storage globals to this engine so any code path picks it up.
    storage_db._bind(eng)  # noqa: SLF001 — explicit test wiring
    yield eng
    eng.dispose()


@pytest.fixture()
def api_session(api_engine: Engine) -> Iterator[Session]:
    connection = api_engine.connect()
    transaction = connection.begin()
    factory = sessionmaker(bind=connection, expire_on_commit=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(
    api_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    # Override blob store to a tmp dir; override DB dep to the test session.
    import eci_ingest.blob_store as bs

    monkeypatch.setattr(bs, "_STORE", LocalBlobStore(tmp_path / "blobs"))

    app = create_app()

    def _override_db() -> Iterator[Session]:
        try:
            yield api_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
