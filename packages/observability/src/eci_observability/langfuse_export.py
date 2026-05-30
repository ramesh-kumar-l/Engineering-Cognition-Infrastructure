"""Langfuse client wrapper.

We isolate Langfuse behind a thin wrapper so:
1. The rest of the codebase imports a stable surface.
2. When unconfigured (no keys), the wrapper is a no-op — never raises.
3. Vendor swaps later require changing only this file.

This file does **not** make any network calls at import time.
"""

from __future__ import annotations

import logging
from typing import Any

from eci_observability.config import ObservabilityConfig

_logger = logging.getLogger(__name__)
_SINGLETON: "LangfuseClient | None" = None


class LangfuseClient:
    """Thin wrapper. ``enabled=False`` means every method is a no-op."""

    def __init__(self, enabled: bool, host: str | None = None) -> None:
        self.enabled = enabled
        self.host = host
        self._client: Any = None
        if not enabled:
            return
        try:
            from langfuse import Langfuse  # type: ignore[import-not-found]
        except ImportError:
            _logger.warning("langfuse.import_failed; running disabled")
            self.enabled = False
            return
        self._client = Langfuse(host=host)
        _logger.info("langfuse.enabled", extra={"host": host})

    def trace(self, name: str, **kwargs: Any) -> Any:
        """Open a Langfuse trace. No-op when disabled."""
        if not self.enabled or self._client is None:
            return _NoopSpan()
        return self._client.trace(name=name, **kwargs)

    def flush(self) -> None:
        """Flush pending spans. No-op when disabled."""
        if self.enabled and self._client is not None:
            self._client.flush()


class _NoopSpan:
    """Returned when Langfuse is disabled."""

    def __getattr__(self, _: str) -> Any:
        return self

    def __call__(self, *_: Any, **__: Any) -> "_NoopSpan":
        return self


def get_langfuse(config: ObservabilityConfig | None = None) -> LangfuseClient:
    """Return the singleton Langfuse client. Constructed lazily."""
    global _SINGLETON
    if _SINGLETON is not None:
        return _SINGLETON
    from eci_observability.config import load_config

    cfg = config or load_config()
    _SINGLETON = LangfuseClient(enabled=cfg.langfuse_enabled, host=cfg.langfuse_host)
    return _SINGLETON
