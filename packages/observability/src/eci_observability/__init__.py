"""ECI observability spine.

Public surface — anything not exported here is private to the package.
"""

from eci_observability.config import ObservabilityConfig, load_config
from eci_observability.langfuse_export import LangfuseClient, get_langfuse
from eci_observability.logging import bind_trace_id, get_logger, setup_logging
from eci_observability.metrics import (
    ingest_bytes,
    ingest_counter,
    request_counter,
    setup_metrics,
    start_metrics_server,
)
from eci_observability.tracing import get_tracer, setup_tracing, shutdown_tracing


def bootstrap(config: ObservabilityConfig | None = None) -> ObservabilityConfig:
    """Initialize tracing, metrics, logging, and Langfuse from config.

    Idempotent — safe to call multiple times. Returns the resolved config so
    callers can introspect what was activated.
    """
    cfg = config or load_config()
    setup_logging(cfg)
    setup_tracing(cfg)
    setup_metrics(cfg)
    get_langfuse(cfg)  # warm singleton; no-op if unconfigured
    return cfg


__all__ = [
    "LangfuseClient",
    "ObservabilityConfig",
    "bind_trace_id",
    "bootstrap",
    "get_langfuse",
    "get_logger",
    "get_tracer",
    "ingest_bytes",
    "ingest_counter",
    "load_config",
    "request_counter",
    "setup_logging",
    "setup_metrics",
    "setup_tracing",
    "shutdown_tracing",
    "start_metrics_server",
]
