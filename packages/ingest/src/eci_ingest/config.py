"""Ingest config."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ECI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    blob_root: Path = Path("./data/blobs")
    ingest_max_bytes: int = 10 * 1024 * 1024  # 10 MiB


def load_ingest_config() -> IngestConfig:
    return IngestConfig()
