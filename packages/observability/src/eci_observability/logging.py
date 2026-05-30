"""Structured logging with trace correlation.

- Console-rendered logs locally; JSON in non-local envs.
- Every log line carries ``trace_id`` / ``span_id`` when emitted inside a span.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from opentelemetry import trace
from structlog.typing import EventDict, WrappedLogger

from eci_observability.config import ObservabilityConfig

_CONFIGURED = False


def _add_trace_correlation(
    _: WrappedLogger, __: str, event_dict: EventDict
) -> EventDict:
    """Attach the current OpenTelemetry trace_id/span_id, if any."""
    span = trace.get_current_span()
    ctx = span.get_span_context() if span else None
    if ctx and ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def setup_logging(config: ObservabilityConfig) -> None:
    """Configure structlog + stdlib logging.

    Idempotent. JSON in non-local envs; console-rendered in local.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, config.log_level, logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_trace_correlation,
        structlog.processors.StackInfoRenderer(),
    ]
    if config.is_local:
        processors.append(structlog.dev.ConsoleRenderer(colors=False))
    else:
        processors.append(structlog.processors.format_exc_info)
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _CONFIGURED = True


def get_logger(name: str = "eci") -> Any:
    """Return a structlog bound logger."""
    return structlog.get_logger(name)


def bind_trace_id(trace_id: str) -> None:
    """Bind an external trace_id to the contextvar (e.g., from inbound header)."""
    structlog.contextvars.bind_contextvars(trace_id=trace_id)
