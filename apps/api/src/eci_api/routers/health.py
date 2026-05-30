"""Liveness and readiness endpoints.

- ``/healthz`` — process is alive.
- ``/readyz`` — process is ready to serve (DB reachable in P2+).
"""

from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel

from eci_observability import request_counter

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/healthz", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def healthz() -> HealthResponse:
    request_counter.labels(route="/healthz", method="GET", outcome="ok").inc()
    return HealthResponse(status="ok", service="eci-api", version="0.1.0")


@router.get("/readyz", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def readyz() -> HealthResponse:
    """Readiness probe. P2+ will verify DB connectivity here."""
    request_counter.labels(route="/readyz", method="GET", outcome="ok").inc()
    return HealthResponse(status="ready", service="eci-api", version="0.1.0")
