"""End-to-end smoke check for the observability spine.

Run: ``make smoke`` (or ``uv run python scripts/smoke.py``).

Produces:
- one OpenTelemetry trace (console exporter unless OTLP configured)
- one Prometheus counter increment (visible at /metrics if API is up)
- one structured log line, trace-correlated.

Exits 0 on success; non-zero on any failure.
"""

from __future__ import annotations

import sys

from eci_observability import (
    bootstrap,
    get_logger,
    get_tracer,
    request_counter,
    shutdown_tracing,
)


def main() -> int:
    cfg = bootstrap()
    log = get_logger("smoke")
    tracer = get_tracer("smoke")

    with tracer.start_as_current_span("smoke.run") as span:
        span.set_attribute("smoke.purpose", "verify-observability-wiring")
        request_counter.labels(route="/smoke", method="CLI", outcome="ok").inc()
        log.info(
            "smoke.completed",
            env=cfg.env,
            tracing_exporter="console" if cfg.tracing_uses_console else "otlp",
            langfuse_enabled=cfg.langfuse_enabled,
        )

    shutdown_tracing()
    return 0


if __name__ == "__main__":
    sys.exit(main())
