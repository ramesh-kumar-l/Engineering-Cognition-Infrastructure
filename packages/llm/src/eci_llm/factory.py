"""Provider factory — driven entirely by LLMConfig; no code edits required to switch providers."""

from __future__ import annotations

from eci_llm.config import LLMConfig, load_llm_config
from eci_llm.errors import LLMError
from eci_llm.protocol import EmbeddingProvider, LLMProvider
from eci_llm.providers.ollama import OllamaEmbeddingProvider, OllamaProvider


def create_llm_provider(config: LLMConfig | None = None) -> LLMProvider:
    """Instantiate the LLM provider selected by *config*."""
    cfg = config or load_llm_config()

    if cfg.provider == "ollama":
        return OllamaProvider(
            host=cfg.ollama_host, model=cfg.model, timeout=cfg.ollama_timeout
        )
    if cfg.provider == "openai":
        if not cfg.openai_api_key:
            raise LLMError("ECI_LLM_OPENAI_API_KEY is required for provider=openai")
        from eci_llm.providers.openai import OpenAIProvider

        return OpenAIProvider(api_key=cfg.openai_api_key, model=cfg.model)
    if cfg.provider == "anthropic":
        if not cfg.anthropic_api_key:
            raise LLMError("ECI_LLM_ANTHROPIC_API_KEY is required for provider=anthropic")
        from eci_llm.providers.anthropic import AnthropicProvider

        return AnthropicProvider(api_key=cfg.anthropic_api_key, model=cfg.model)
    if cfg.provider == "openrouter":
        if not cfg.openrouter_api_key:
            raise LLMError("ECI_LLM_OPENROUTER_API_KEY is required for provider=openrouter")
        from eci_llm.providers.openrouter import OpenRouterProvider

        return OpenRouterProvider(api_key=cfg.openrouter_api_key, model=cfg.model)
    raise LLMError(f"Unknown LLM provider: {cfg.provider!r}")  # guarded by Literal


def create_embedding_provider(config: LLMConfig | None = None) -> EmbeddingProvider:
    """Instantiate the embedding provider selected by *config*."""
    cfg = config or load_llm_config()

    if cfg.embedding_provider == "ollama":
        return OllamaEmbeddingProvider(
            host=cfg.ollama_host,
            model=cfg.embedding_model,
            dimensions=cfg.embedding_dim,
            timeout=cfg.ollama_timeout,
        )
    if cfg.embedding_provider == "openai":
        if not cfg.openai_api_key:
            raise LLMError("ECI_LLM_OPENAI_API_KEY is required for embedding_provider=openai")
        from eci_llm.providers.openai import OpenAIEmbeddingProvider

        return OpenAIEmbeddingProvider(
            api_key=cfg.openai_api_key,
            model=cfg.embedding_model,
            dimensions=cfg.embedding_dim,
        )
    raise LLMError(f"Unknown embedding provider: {cfg.embedding_provider!r}")
