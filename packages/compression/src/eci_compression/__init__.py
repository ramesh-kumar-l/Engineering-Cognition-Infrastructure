"""eci-compression — knowledge compression pipeline.

Public surface:
- ``CompressionService`` — orchestrates summarize + mental-model + playbook.
- ``SummarizationService``, ``MentalModelService``, ``PlaybookService`` — individual stages.
- ``TextChunker`` — text chunking utility (Phase 4 embedding preparation).
- DTOs: ``CompressionRequest``, ``CompressionResult``, ``SummaryLevel``, ``SourceType``.
- ``CompressionConfig``, ``load_compression_config``.
- Errors: ``CompressionError``, ``SourceNotFound``, ``ContentTooLarge``, ``ParseOutputError``.
"""

from eci_compression.chunker import TextChunker
from eci_compression.compression_service import CompressionService
from eci_compression.config import CompressionConfig, load_compression_config
from eci_compression.dto import (
    CompressionRequest,
    CompressionResult,
    EntityRecord,
    MentalModelResult,
    PlaybookResult,
    RelationshipRecord,
    SourceType,
    SummaryLevel,
    SummaryResult,
)
from eci_compression.errors import (
    CompressionError,
    ContentTooLarge,
    ParseOutputError,
    SourceNotFound,
)
from eci_compression.mental_model import MentalModelService
from eci_compression.playbook import PlaybookService
from eci_compression.summarizer import SummarizationService

__all__ = [
    "TextChunker",
    "CompressionService",
    "CompressionConfig",
    "load_compression_config",
    "CompressionRequest",
    "CompressionResult",
    "EntityRecord",
    "MentalModelResult",
    "PlaybookResult",
    "RelationshipRecord",
    "SourceType",
    "SummaryLevel",
    "SummaryResult",
    "CompressionError",
    "ContentTooLarge",
    "ParseOutputError",
    "SourceNotFound",
    "MentalModelService",
    "PlaybookService",
    "SummarizationService",
]
