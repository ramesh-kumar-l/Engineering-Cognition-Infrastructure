"""LLM runtime configuration — env prefix ECI_LLM_."""

from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ProviderName = Literal["ollama", "openai", "anthropic", "openrouter"]
EmbeddingProviderName = Literal["ollama", "openai"]


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ECI_LLM_", env_file=".env", extra="ignore")

    # LLM provider
    provider: ProviderName = Field(default="ollama")
    model: str = Field(default="llama3.2")
    max_tokens: int = Field(default=2048)
    temperature: float = Field(default=0.1)

    # Embedding provider
    embedding_provider: EmbeddingProviderName = Field(default="ollama")
    embedding_model: str = Field(default="nomic-embed-text")
    embedding_dim: int = Field(default=768)

    # Ollama settings
    ollama_host: str = Field(default="http://localhost:11434")
    ollama_timeout: float = Field(default=120.0)

    # Cloud API keys (optional; not required for offline path)
    openai_api_key: str | None = Field(default=None)
    anthropic_api_key: str | None = Field(default=None)
    openrouter_api_key: str | None = Field(default=None)


_config: LLMConfig | None = None


def load_llm_config() -> LLMConfig:
    global _config
    if _config is None:
        _config = LLMConfig()
    return _config
