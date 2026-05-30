"""Health endpoint contract tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from eci_api.main import create_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_healthz_returns_ok(client: TestClient) -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "eci-api"


def test_readyz_returns_ready(client: TestClient) -> None:
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_metrics_endpoint_serves_text(client: TestClient) -> None:
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    assert b"eci_requests_total" in r.content
