"""FastAPI dependency providers — DB session, blob store, services."""

from __future__ import annotations

from collections.abc import Iterator

from eci_compression.compression_service import CompressionService
from eci_execution.goal_service import GoalService
from eci_execution.roadmap_service import RoadmapService
from eci_execution.task_service import TaskService
from eci_identity.tenant_service import TenantService
from eci_identity.user_service import UserService
from eci_ingest import (
    DocumentIngestService,
    NoteIngestService,
    SourceReadService,
    get_blob_store,
)
from eci_llm import EmbeddingProvider, LLMProvider, create_embedding_provider, create_llm_provider
from eci_reflection.lesson_service import LessonService
from eci_reflection.retrospective_service import RetrospectiveService
from eci_retrieval.assistant_service import AssistantService
from eci_retrieval.embedding_service import EmbeddingService
from eci_retrieval.hybrid_retriever import HybridRetriever
from eci_retrieval.memory_service import MemoryService
from eci_storage import sessionmaker_for
from fastapi import Depends
from sqlalchemy.orm import Session

# Process-level provider singletons (created on first request).
_llm_provider: LLMProvider | None = None
_embedding_provider: EmbeddingProvider | None = None


def get_db() -> Iterator[Session]:
    """Yield a Session, commit on success, rollback on error."""
    factory = sessionmaker_for()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_llm_provider() -> LLMProvider:
    """Return the process-level LLM provider. Created once on first call."""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = create_llm_provider()
    return _llm_provider


def get_embedding_provider() -> EmbeddingProvider:
    """Return the process-level embedding provider. Created once on first call."""
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = create_embedding_provider()
    return _embedding_provider


def get_document_service(
    session: Session = Depends(get_db),
) -> DocumentIngestService:
    return DocumentIngestService(session, blob_store=get_blob_store())


def get_note_service(session: Session = Depends(get_db)) -> NoteIngestService:
    return NoteIngestService(session)


def get_source_read_service(session: Session = Depends(get_db)) -> SourceReadService:
    return SourceReadService(session)


def get_compression_service(
    session: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_llm_provider),
) -> CompressionService:
    return CompressionService(session, provider)


def get_embedding_service(
    session: Session = Depends(get_db),
    provider: EmbeddingProvider = Depends(get_embedding_provider),
) -> EmbeddingService:
    return EmbeddingService(session, provider)


def get_hybrid_retriever(
    session: Session = Depends(get_db),
    provider: EmbeddingProvider = Depends(get_embedding_provider),
) -> HybridRetriever:
    return HybridRetriever(session, provider)


def get_memory_service(
    session: Session = Depends(get_db),
    provider: EmbeddingProvider = Depends(get_embedding_provider),
) -> MemoryService:
    return MemoryService(session, provider)


def get_assistant_service(
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    provider: LLMProvider = Depends(get_llm_provider),
) -> AssistantService:
    return AssistantService(retriever, provider)


def get_goal_service(session: Session = Depends(get_db)) -> GoalService:
    return GoalService(session)


def get_task_service(session: Session = Depends(get_db)) -> TaskService:
    return TaskService(session)


def get_roadmap_service(session: Session = Depends(get_db)) -> RoadmapService:
    return RoadmapService(session)


def get_lesson_service(session: Session = Depends(get_db)) -> LessonService:
    return LessonService(session)


def get_retrospective_service(
    session: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_llm_provider),
) -> RetrospectiveService:
    return RetrospectiveService(session, provider)


def get_tenant_service(session: Session = Depends(get_db)) -> TenantService:
    return TenantService(session)


def get_user_service(session: Session = Depends(get_db)) -> UserService:
    return UserService(session)
