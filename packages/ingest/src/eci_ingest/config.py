"""Ingest config."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

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

    # S3 adapter (P8) — activated by ECI_BLOB_BACKEND=s3
    blob_backend: Literal["local", "s3"] = "local"
    blob_s3_bucket: str = ""
    blob_s3_prefix: str = "blobs/"
    blob_s3_region: str = "us-east-1"
    blob_s3_endpoint_url: str = ""  # non-empty for MinIO / local S3-compat


def load_ingest_config() -> IngestConfig:
    return IngestConfig()
