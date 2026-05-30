"""Compression configuration — env prefix ECI_COMPRESSION_."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CompressionConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ECI_COMPRESSION_", env_file=".env", extra="ignore"
    )

    # Hard limit on content fed to the LLM (characters).
    # Prevents context-window overflow; content beyond this is truncated.
    max_content_chars: int = Field(default=32_000)

    # Chunk parameters — used for embedding preparation in Phase 4.
    chunk_size_chars: int = Field(default=1_000)
    chunk_overlap_chars: int = Field(default=100)

    # Whether to attempt playbook extraction on every document.
    extract_playbooks: bool = Field(default=True)


_config: CompressionConfig | None = None


def load_compression_config() -> CompressionConfig:
    global _config
    if _config is None:
        _config = CompressionConfig()
    return _config
