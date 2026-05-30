"""Storage env config — single source of truth for DB URLs."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ECI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_url: str = "postgresql+psycopg://eci:eci@localhost:5432/eci"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_pre_ping: bool = True
    db_echo: bool = False


def load_storage_config() -> StorageConfig:
    return StorageConfig()
