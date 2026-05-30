"""Observability config loaded from environment.

Keep this file small — it is the single source of truth for env var names.
Any new env var lives here, *not* scattered across modules.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Env = Literal["local", "dev", "prod"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ObservabilityConfig(BaseSettings):
    """Environment-driven configuration.

    Defaults are tuned for local development:
    - No OTLP endpoint → console exporter (proves wiring without infra).
    - No Langfuse keys → Langfuse is a no-op.
    """

    model_config = SettingsConfigDict(
        env_prefix="ECI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Env = "local"
    log_level: LogLevel = "INFO"
    service_name: str = "eci-api"
    service_version: str = "0.1.0"

    # Tracing
    otlp_endpoint: str | None = None  # unset → console exporter
    otlp_insecure: bool = True

    # Metrics
    prometheus_port: int = Field(default=9464, ge=1, le=65535)
    metrics_path: str = "/metrics"

    # Langfuse (optional)
    langfuse_host: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None

    @property
    def is_local(self) -> bool:
        return self.env == "local"

    @property
    def tracing_uses_console(self) -> bool:
        return self.otlp_endpoint is None

    @property
    def langfuse_enabled(self) -> bool:
        return bool(
            self.langfuse_host
            and self.langfuse_public_key
            and self.langfuse_secret_key
        )


def load_config() -> ObservabilityConfig:
    """Load config from env. Cached at the module boundary by callers if needed."""
    return ObservabilityConfig()
