"""OpenTelemetry tracing setup.

Single entry: ``setup_tracing(config)``. Returns the configured ``TracerProvider``.
Idempotent — calling it twice does not double-register.
"""

from __future__ import annotations

import logging
from typing import cast

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanExporter,
)
from opentelemetry.trace import Tracer

from eci_observability.config import ObservabilityConfig

_logger = logging.getLogger(__name__)
_PROVIDER: TracerProvider | None = None


def setup_tracing(config: ObservabilityConfig) -> TracerProvider:
    """Configure the global TracerProvider.

    - Local / no OTLP endpoint → ConsoleSpanExporter (stdout).
    - OTLP endpoint set → BatchSpanProcessor with OTLPSpanExporter.
    """
    global _PROVIDER
    if _PROVIDER is not None:
        return _PROVIDER

    resource = Resource.create(
        {
            "service.name": config.service_name,
            "service.version": config.service_version,
            "deployment.environment": config.env,
        }
    )
    provider = TracerProvider(resource=resource)

    exporter: SpanExporter
    if config.tracing_uses_console:
        exporter = ConsoleSpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        _logger.info("tracing.console_exporter")
    else:
        endpoint = cast(str, config.otlp_endpoint)
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=config.otlp_insecure)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        _logger.info("tracing.otlp_exporter", extra={"endpoint": endpoint})

    trace.set_tracer_provider(provider)
    _PROVIDER = provider
    return provider


def get_tracer(name: str = "eci") -> Tracer:
    """Return a tracer; assumes :func:`setup_tracing` has run."""
    return trace.get_tracer(name)


def shutdown_tracing() -> None:
    """Flush and shutdown the provider. Useful in scripts/tests."""
    global _PROVIDER
    if _PROVIDER is not None:
        _PROVIDER.shutdown()
        _PROVIDER = None
