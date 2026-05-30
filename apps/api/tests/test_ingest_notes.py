"""API integration tests for the notes ingest endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_create_note_returns_201(client: TestClient) -> None:
    r = client.post(
        "/notes",
        json={"body": "a thought", "source": "manual", "tags": ["t"]},
    )
    assert r.status_code == 201, r.text
    assert r.json()["deduplicated"] is False


@pytest.mark.integration
def test_dedup_on_replay(client: TestClient) -> None:
    payload = {"body": "same", "source": "manual", "author": "me"}
    a = client.post("/notes", json=payload).json()
    b = client.post("/notes", json=payload).json()
    assert a["id"] == b["id"]
    assert b["deduplicated"] is True


@pytest.mark.integration
def test_empty_body_rejected(client: TestClient) -> None:
    r = client.post("/notes", json={"body": "", "source": "m"})
    assert r.status_code == 422
