"""EmbeddingService — chunks source content and stores per-chunk embeddings."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_compression.chunker import TextChunker
from eci_llm.protocol import EmbeddingProvider, EmbeddingRequest
from eci_observability import get_logger
from eci_retrieval.config import RetrievalConfig
from eci_retrieval.errors import EmbeddingError, SourceNotFoundError
from eci_storage.models import ChunkEmbedding, Document, Note

_log = get_logger("eci_retrieval.embedding_service")


class EmbeddingService:
    def __init__(
        self,
        session: Session,
        provider: EmbeddingProvider,
        config: RetrievalConfig | None = None,
    ) -> None:
        self._session = session
        self._provider = provider
        self._config = config or RetrievalConfig()
        self._chunker = TextChunker(
            chunk_size_chars=1000,
            overlap_chars=100,
        )

    def embed_document(self, document_id: uuid.UUID) -> int:
        """Chunk and embed a document. Idempotent — skips already-embedded chunks."""
        doc = self._session.get(Document, document_id)
        if doc is None:
            raise SourceNotFoundError(f"Document {document_id} not found")
        return self._embed_source(
            source_id=document_id,
            source_type="document",
            content=doc.body,
            doc_id=document_id,
            note_id=None,
        )

    def embed_note(self, note_id: uuid.UUID) -> int:
        """Chunk and embed a note. Idempotent — skips already-embedded chunks."""
        note = self._session.get(Note, note_id)
        if note is None:
            raise SourceNotFoundError(f"Note {note_id} not found")
        return self._embed_source(
            source_id=note_id,
            source_type="note",
            content=note.body,
            doc_id=None,
            note_id=note_id,
        )

    def embed_text(self, text: str) -> list[float]:
        """Embed a single string. Used for query encoding at search time."""
        try:
            resp = self._provider.embed(EmbeddingRequest(texts=[text]))
            return resp.embeddings[0]
        except Exception as exc:
            raise EmbeddingError(f"Failed to embed query: {exc}") from exc

    def _embed_source(
        self,
        source_id: uuid.UUID,
        source_type: str,
        content: str,
        doc_id: uuid.UUID | None,
        note_id: uuid.UUID | None,
    ) -> int:
        chunks = self._chunker.chunk(content, str(source_id))
        if not chunks:
            _log.warning("embedding.no_chunks", source_type=source_type, source_id=str(source_id))
            return 0

        existing_hashes = {
            row
            for (row,) in self._session.execute(
                select(ChunkEmbedding.content_hash).where(
                    (ChunkEmbedding.document_id == doc_id)
                    if doc_id
                    else (ChunkEmbedding.note_id == note_id)
                )
            )
        }

        new_chunks = [c for c in chunks if c.content_hash not in existing_hashes]
        if not new_chunks:
            _log.info(
                "embedding.skipped_all_cached",
                source_type=source_type,
                source_id=str(source_id),
                count=len(chunks),
            )
            return 0

        try:
            resp = self._provider.embed(EmbeddingRequest(texts=[c.content for c in new_chunks]))
        except Exception as exc:
            raise EmbeddingError(f"Embedding provider failed: {exc}") from exc

        for chunk, vec in zip(new_chunks, resp.embeddings):
            self._session.add(
                ChunkEmbedding(
                    document_id=doc_id,
                    note_id=note_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    content_hash=chunk.content_hash,
                    embedding=vec,
                    model_used=self._provider.model_name,
                    dimensions=self._provider.dimensions,
                )
            )

        self._session.flush()
        _log.info(
            "embedding.done",
            source_type=source_type,
            source_id=str(source_id),
            new_chunks=len(new_chunks),
        )
        return len(new_chunks)
