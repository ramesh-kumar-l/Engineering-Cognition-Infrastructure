"""eci-llm — LLM and Embedding runtime abstraction.

Public surface:
- ``LLMProvider``, ``EmbeddingProvider`` — structural Protocols.
- ``LLMRequest``, ``LLMResponse``, ``EmbeddingRequest``, ``EmbeddingResponse`` — DTOs.
- ``LLMConfig``, ``load_llm_config`` — configuration.
- ``create_llm_provider``, ``create_embedding_provider`` — factory functions.
- ``LLMError``, ``LLMProviderError``, ``LLMParseError``, ``LLMProviderNotAvailable`` — errors.
"""

from eci_llm.config import LLMConfig, load_llm_config
from eci_llm.errors import (
    LLMError,
    LLMParseError,
    LLMProviderError,
    LLMProviderNotAvailable,
)
from eci_llm.factory import create_embedding_provider, create_llm_provider
from eci_llm.protocol import (
    EmbeddingProvider,
    EmbeddingRequest,
    EmbeddingResponse,
    LLMMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)

__all__ = [
    "LLMConfig",
    "load_llm_config",
    "LLMError",
    "LLMParseError",
    "LLMProviderError",
    "LLMProviderNotAvailable",
    "create_llm_provider",
    "create_embedding_provider",
    "EmbeddingProvider",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "LLMMessage",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
]
