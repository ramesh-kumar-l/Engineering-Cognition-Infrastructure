"""Unit tests for the LLM provider factory."""

from __future__ import annotations

import pytest

from eci_llm.config import LLMConfig
from eci_llm.errors import LLMError
from eci_llm.factory import create_embedding_provider, create_llm_provider
from eci_llm.providers.ollama import OllamaEmbeddingProvider, OllamaProvider


def _ollama_cfg(**overrides: object) -> LLMConfig:
    return LLMConfig(
        provider="ollama",
        model="llama3.2",
        embedding_provider="ollama",
        embedding_model="nomic-embed-text",
        embedding_dim=768,
        ollama_host="http://localhost:11434",
        **overrides,  # type: ignore[arg-type]
    )


def test_create_ollama_llm_provider() -> None:
    provider = create_llm_provider(_ollama_cfg())
    assert isinstance(provider, OllamaProvider)
    assert provider.model_name == "llama3.2"


def test_create_ollama_embedding_provider() -> None:
    provider = create_embedding_provider(_ollama_cfg())
    assert isinstance(provider, OllamaEmbeddingProvider)
    assert provider.dimensions == 768
    assert provider.model_name == "nomic-embed-text"


def test_openai_requires_api_key() -> None:
    cfg = LLMConfig(provider="openai", openai_api_key=None)
    with pytest.raises(LLMError, match="OPENAI_API_KEY"):
        create_llm_provider(cfg)


def test_anthropic_requires_api_key() -> None:
    cfg = LLMConfig(provider="anthropic", anthropic_api_key=None)
    with pytest.raises(LLMError, match="ANTHROPIC_API_KEY"):
        create_llm_provider(cfg)


def test_openrouter_requires_api_key() -> None:
    cfg = LLMConfig(provider="openrouter", openrouter_api_key=None)
    with pytest.raises(LLMError, match="OPENROUTER_API_KEY"):
        create_llm_provider(cfg)


def test_openai_embedding_requires_api_key() -> None:
    cfg = LLMConfig(embedding_provider="openai", openai_api_key=None)
    with pytest.raises(LLMError, match="OPENAI_API_KEY"):
        create_embedding_provider(cfg)
