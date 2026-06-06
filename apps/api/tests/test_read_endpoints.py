"""API integration tests for source read endpoints (Document Viewer backend).

Real Postgres (via ECI_TEST_DB_URL). Auth is supplied by overriding
``get_request_context`` so we can drive tenant isolation explicitly.
"""

from __future__ import annotations

import io
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from eci_api.auth import get_request_context
from eci_api.dependencies import get_db
from eci_api.main import create_app
from eci_identity.dto import RequestContext
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _ctx(tenant_id: uuid.UUID) -> RequestContext:
    return RequestContext(
        user_id=uuid.uuid4(), tenant_id=tenant_id, role="admin", actor="test@local"
    )


@pytest.fixture
def tenants(api_session: Session) -> tuple[uuid.UUID, uuid.UUID]:
    """Two real tenants — documents.tenant_id is a FK to tenants.id."""
    from eci_storage.models import Tenant

    suffix = uuid.uuid4().hex[:8]
    a = Tenant(name="A", slug=f"tenant-a-{suffix}")
    b = Tenant(name="B", slug=f"tenant-b-{suffix}")
    api_session.add_all([a, b])
    api_session.flush()
    return a.id, b.id


@pytest.fixture
def ctx_holder(tenants: tuple[uuid.UUID, uuid.UUID]) -> dict[str, RequestContext]:
    return {"ctx": _ctx(tenants[0])}


@pytest.fixture
def rclient(
    api_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ctx_holder: dict[str, RequestContext],
) -> Iterator[TestClient]:
    import eci_ingest.blob_store as bs
    from eci_ingest.blob_store import LocalBlobStore

    monkeypatch.setattr(bs, "_STORE", LocalBlobStore(tmp_path / "blobs"))
    app = create_app()

    def _override_db() -> Iterator[Session]:
        yield api_session

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_request_context] = lambda: ctx_holder["ctx"]
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _ingest_doc(client: TestClient, body: bytes = b"# Title\n\nhello world") -> str:
    r = client.post(
        "/documents",
        data={"kind": "markdown", "source": "test", "title": "Title"},
        files={"file": ("doc.md", io.BytesIO(body), "text/markdown")},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest.mark.integration
def test_get_document_returns_body(rclient: TestClient) -> None:
    doc_id = _ingest_doc(rclient)
    r = rclient.get(f"/documents/{doc_id}")
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload["id"] == doc_id
    assert "hello world" in payload["body"]
    assert payload["content_hash"]


@pytest.mark.integration
def test_list_documents_includes_ingested(rclient: TestClient) -> None:
    doc_id = _ingest_doc(rclient)
    r = rclient.get("/documents")
    assert r.status_code == 200
    ids = [d["id"] for d in r.json()]
    assert doc_id in ids


@pytest.mark.integration
def test_get_missing_document_404(rclient: TestClient) -> None:
    r = rclient.get(f"/documents/{uuid.uuid4()}")
    assert r.status_code == 404


@pytest.mark.integration
def test_cross_tenant_document_is_not_found(
    rclient: TestClient,
    ctx_holder: dict[str, RequestContext],
    tenants: tuple[uuid.UUID, uuid.UUID],
) -> None:
    # Ingest as tenant A.
    doc_id = _ingest_doc(rclient)
    # Switch to tenant B; the document must be invisible.
    ctx_holder["ctx"] = _ctx(tenants[1])
    r = rclient.get(f"/documents/{doc_id}")
    assert r.status_code == 404
    assert doc_id not in [d["id"] for d in rclient.get("/documents").json()]
