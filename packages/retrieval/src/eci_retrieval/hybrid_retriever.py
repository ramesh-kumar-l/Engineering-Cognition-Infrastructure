"""HybridRetriever — orchestrates FTS + vector search, RRF rerank, citation build."""

from __future__ import annotations

from sqlalchemy.orm import Session

from eci_llm.protocol import EmbeddingProvider
from eci_observability import get_logger
from eci_retrieval.citation_engine import CitationEngine
from eci_retrieval.config import RetrievalConfig, load_retrieval_config
from eci_retrieval.dto import RetrievalRequest, RetrievalResult
from eci_retrieval.embedding_service import EmbeddingService
from eci_retrieval.fts_service import FTSService
from eci_retrieval.reranker import RRFReranker
from eci_retrieval.vector_service import VectorService

_log = get_logger("eci_retrieval.hybrid_retriever")


class HybridRetriever:
    """Production hybrid retriever: BM25 + pgvector + RRF rerank + citation enrichment."""

    def __init__(
        self,
        session: Session,
        embedding_provider: EmbeddingProvider,
        config: RetrievalConfig | None = None,
    ) -> None:
        self._config = config or load_retrieval_config()
        self._embedding_service = EmbeddingService(session, embedding_provider, self._config)
        self._fts = FTSService(session)
        self._vector = VectorService(session, self._embedding_service)
        self._reranker = RRFReranker(k=self._config.rrf_k)
        self._citation_engine = CitationEngine(session)

    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """Run hybrid retrieval and return a citable RetrievalResult."""
        _log.info("retrieval.start", query=request.query[:120], top_k=request.top_k)

        fts_hits = self._fts.search(
            request.query, top_k=self._config.rerank_top_k, tenant_id=request.tenant_id
        )
        vector_hits = self._vector.search(
            request.query, top_k=self._config.rerank_top_k, tenant_id=request.tenant_id
        )

        reranked = self._reranker.rerank(fts_hits, vector_hits, top_k=request.top_k)

        # Filter by source type if caller restricted it
        if request.source_types and len(request.source_types) < 2:
            reranked = [h for h in reranked if h.source_type in request.source_types]

        # Drop results below min_score threshold
        if self._config.min_score > 0.0:
            reranked = [h for h in reranked if h.score >= self._config.min_score]

        citations = self._citation_engine.build_citations(reranked)

        _log.info(
            "retrieval.done",
            query=request.query[:120],
            fts_hits=len(fts_hits),
            vector_hits=len(vector_hits),
            citations=len(citations),
        )

        return RetrievalResult(
            query=request.query,
            citations=citations,
            retrieval_stages={
                "fts": len(fts_hits),
                "vector": len(vector_hits),
                "reranked": len(reranked),
                "returned": len(citations),
            },
        )
