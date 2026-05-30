"""API integration tests for the documents ingest endpoint."""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_ingest_markdown_returns_201(client: TestClient) -> None:
    body = b"# Title\n\nbody"
    r = client.post(
        "/documents",
        data={"kind": "markdown", "source": "test", "tags": "a,b"},
        files={"file": ("doc.md", io.BytesIO(body), "text/markdown")},
    )
    assert r.status_code == 201, r.text
    payload = r.json()
    assert payload["title"] == "Title"
    assert payload["deduplicated"] is False


@pytest.mark.integration
def test_reingest_same_content_dedup(client: TestClient) -> None:
    body = b"# Same\n\nbody"
    for _ in range(2):
        r = client.post(
            "/documents",
            data={"kind": "markdown", "source": "test"},
            files={"file": ("doc.md", io.BytesIO(body), "text/markdown")},
        )
        assert r.status_code == 201
    assert r.json()["deduplicated"] is True


@pytest.mark.integration
def test_unsupported_kind_returns_415(client: TestClient) -> None:
    r = client.post(
        "/documents",
        data={"kind": "docx", "source": "test"},
        files={"file": ("x.docx", io.BytesIO(b"x"), "application/x-docx")},
    )
    # The DTO validation rejects "docx" via Literal → 422 before we reach the
    # service. Both 415 and 422 are acceptable; document the boundary.
    assert r.status_code in (415, 422)
