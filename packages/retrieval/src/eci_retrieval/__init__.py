"""eci-retrieval — hybrid retrieval, citation engine, long-term memory (Phase 4).

Public surface:
- ``HybridRetriever`` — BM25 + pgvector + RRF rerank.
- ``EmbeddingService`` — chunk + embed documents/notes.
- ``MemoryService`` — long-term memory CRUD + vector search.
- ``RetrievalRequest``, ``RetrievalResult``, ``Citation`` — result DTOs.
- ``MemoryEntryInput``, ``MemoryEntryOut`` — memory DTOs.
- ``RetrievalError``, ``NoCitationError``, ``EmbeddingError`` — errors.
"""

from eci_retrieval.config import RetrievalConfig, load_retrieval_config
from eci_retrieval.dto import (
    ChunkHit,
    Citation,
    MemoryEntryInput,
    MemoryEntryOut,
    RetrievalRequest,
    RetrievalResult,
)
from eci_retrieval.embedding_service import EmbeddingService
from eci_retrieval.errors import EmbeddingError, NoCitationError, RetrievalError, SourceNotFoundError
from eci_retrieval.hybrid_retriever import HybridRetriever
from eci_retrieval.memory_service import MemoryService

__all__ = [
    "RetrievalConfig",
    "load_retrieval_config",
    "ChunkHit",
    "Citation",
    "MemoryEntryInput",
    "MemoryEntryOut",
    "RetrievalRequest",
    "RetrievalResult",
    "EmbeddingService",
    "EmbeddingError",
    "NoCitationError",
    "RetrievalError",
    "SourceNotFoundError",
    "HybridRetriever",
    "MemoryService",
]
