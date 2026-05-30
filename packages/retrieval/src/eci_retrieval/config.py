"""RetrievalConfig — driven by environment variables with prefix ECI_RETRIEVAL_."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetrievalConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ECI_RETRIEVAL_", extra="ignore")

    top_k: int = Field(default=10, description="Max citations returned to the caller.")
    rerank_top_k: int = Field(
        default=20, description="Candidates fetched from each retrieval stage before reranking."
    )
    rrf_k: int = Field(default=60, description="RRF denominator constant.")
    fts_weight: float = Field(default=0.5)
    vector_weight: float = Field(default=0.5)
    min_score: float = Field(default=0.0, description="Drop citations below this score.")
    embedding_dim: int = Field(default=768)


def load_retrieval_config() -> RetrievalConfig:
    return RetrievalConfig()
