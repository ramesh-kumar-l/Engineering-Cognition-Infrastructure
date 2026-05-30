"""Prometheus metrics.

We expose two stable counters from Phase 1:
- ``eci_requests_total`` — incremented per inbound request handler invocation.
- ``eci_ingest_total`` — Phase 2 ingest counter (defined here so the contract
  is centralized; the value is bumped from the ingest service).

Add new metrics by declaring them here, never inline in service code, so the
metric vocabulary stays auditable.
"""

from __future__ import annotations

import logging
import threading

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Histogram,
    start_http_server,
)

from eci_observability.config import ObservabilityConfig

_logger = logging.getLogger(__name__)
_SERVER_STARTED = False
_SERVER_LOCK = threading.Lock()


request_counter = Counter(
    "eci_requests_total",
    "Total inbound requests handled, labelled by route and outcome.",
    labelnames=("route", "method", "outcome"),
    registry=REGISTRY,
)

request_latency_seconds = Histogram(
    "eci_request_latency_seconds",
    "Request handling latency by route.",
    labelnames=("route", "method"),
    registry=REGISTRY,
)

ingest_counter = Counter(
    "eci_ingest_total",
    "Total ingest operations, labelled by source kind and outcome.",
    labelnames=("source_kind", "outcome"),
    registry=REGISTRY,
)

ingest_bytes = Counter(
    "eci_ingest_bytes_total",
    "Total bytes ingested, labelled by source kind.",
    labelnames=("source_kind",),
    registry=REGISTRY,
)


def setup_metrics(config: ObservabilityConfig) -> None:
    """Start the Prometheus HTTP exposition server.

    Idempotent. Bound to all interfaces on ``config.prometheus_port``.
    """
    start_metrics_server(config.prometheus_port)


def start_metrics_server(port: int, registry: CollectorRegistry = REGISTRY) -> None:
    """Start the metrics HTTP server. Safe to call multiple times."""
    global _SERVER_STARTED
    with _SERVER_LOCK:
        if _SERVER_STARTED:
            return
        start_http_server(port, registry=registry)
        _SERVER_STARTED = True
        _logger.info("metrics.server_started", extra={"port": port})
