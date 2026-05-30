"""API-specific config. Observability config lives in eci_observability.config."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiConfig(BaseSettings):
    """API runtime config from env."""

    model_config = SettingsConfigDict(
        env_prefix="ECI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"  # noqa: S104 — container bind is intentional
    port: int = 8000
    cors_origins: list[str] = []


def load_api_config() -> ApiConfig:
    return ApiConfig()
