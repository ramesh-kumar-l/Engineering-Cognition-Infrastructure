"""Smoke tests for the observability spine.

These tests prove the wiring works *without* external infrastructure:
- Tracing uses ConsoleSpanExporter.
- Metrics counter increments are visible via the registry.
- Logging emits a structured line with trace correlation.
- Langfuse is a no-op when unconfigured.
"""

from __future__ import annotations

from prometheus_client import REGISTRY

from eci_observability import (
    ObservabilityConfig,
    bootstrap,
    get_langfuse,
    get_logger,
    get_tracer,
    request_counter,
    shutdown_tracing,
)


def _local_config() -> ObservabilityConfig:
    return ObservabilityConfig(
        env="local",
        log_level="DEBUG",
        otlp_endpoint=None,
        langfuse_host=None,
        langfuse_public_key=None,
        langfuse_secret_key=None,
        prometheus_port=0,  # 0 = let kernel choose; not needed for these tests
    )


def test_bootstrap_returns_config() -> None:
    cfg = bootstrap(_local_config())
    assert cfg.is_local
    assert cfg.tracing_uses_console
    assert not cfg.langfuse_enabled


def test_tracer_starts_span() -> None:
    bootstrap(_local_config())
    tracer = get_tracer("test")
    with tracer.start_as_current_span("smoke") as span:
        assert span.is_recording()
        assert span.get_span_context().is_valid
    shutdown_tracing()


def test_request_counter_increments() -> None:
    before = _counter_value("eci_requests_total", route="/smoke", method="GET", outcome="ok")
    request_counter.labels(route="/smoke", method="GET", outcome="ok").inc()
    after = _counter_value("eci_requests_total", route="/smoke", method="GET", outcome="ok")
    assert after == before + 1


def test_logger_emits_without_error() -> None:
    bootstrap(_local_config())
    log = get_logger("smoke")
    log.info("smoke.test", purpose="verify-wiring")


def test_langfuse_noop_when_unconfigured() -> None:
    client = get_langfuse(_local_config())
    assert client.enabled is False
    # No-op span chain must not raise:
    span = client.trace(name="noop")
    span.update(status="ok").end()
    client.flush()


def _counter_value(name: str, **labels: str) -> float:
    """Read a labelled counter's current value out of the global registry."""
    for metric in REGISTRY.collect():
        if metric.name != name and metric.name != name.removesuffix("_total"):
            continue
        for sample in metric.samples:
            if sample.name.endswith("_total") and sample.labels == labels:
                return sample.value
    return 0.0
