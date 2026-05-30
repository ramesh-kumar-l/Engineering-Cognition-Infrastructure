# ADR-006 — Retrieval Strategy

| Field      | Value                      |
|------------|----------------------------|
| ID         | ADR-006                    |
| Status     | Accepted                   |
| Date       | 2026-05-30                 |
| Author     | ECI Architect              |

## Context

Phase 4 requires production-grade retrieval with evidence. Two complementary retrieval signals are available: full-text search (exact keyword matching, high precision for domain terms) and vector similarity (semantic matching, high recall for paraphrase and related concepts). Neither alone is sufficient.

A cross-encoder reranker (ML model) would improve precision at the top of the ranked list, but introduces: a new ML runtime dependency, GPU/CPU inference latency, and an offline-first risk (AP-3).

## Decision

**Hybrid retrieval = BM25 (Postgres FTS) + pgvector (cosine) + RRF rerank.**

1. **BM25** — implemented via Postgres `tsvector` / `websearch_to_tsquery` / `ts_rank_cd`. GIN index on `chunk_embeddings.content`. No extra process, no extra dependency.

2. **pgvector HNSW** — cosine distance index on `chunk_embeddings.embedding` (768-dim, `nomic-embed-text` via Ollama default). HNSW is chosen over IVFFlat because it requires no pre-build data and performs better at small-to-medium corpus sizes.

3. **RRF (Reciprocal Rank Fusion)** — Cormack et al. (2009). `score = Σ 1/(k + rank)` with `k=60`. No ML model, fully offline, provably effective for fusing heterogeneous ranked lists. A neural cross-encoder can be plugged in as a post-RRF reranker in a future phase without changing the retrieval contract.

4. **Citation enforcement** — every `RetrievalResult` carries `citations: list[Citation]`. Empty citations are surfaced explicitly (`has_citations=False`) rather than returning a synthetic answer — AP-2 ("evidence before inference").

5. **Long-term memory** (`memory_entries` table) — distinct from raw ingest. Curated, versioned, back-linked to source documents/notes. Vector-indexed with the same HNSW pattern.

## Consequences

- AP-3 (offline-first) satisfied: Ollama provides embeddings; all retrieval is in-process Postgres.
- AP-2 satisfied: retrieval results are structurally forced to carry citations.
- Cross-encoder reranker deferred: acceptable for P4 corpus sizes; revisit at P6 when the lesson corpus is large enough to measure reranker uplift.
- FTS requires text chunking first — embedding must run before full retrieval is available for a given source.
- `pgvector>=0.5` required (HNSW support); confirmed available in `pgvector/pgvector:pg16` Docker image.

## Alternatives Rejected

| Option | Why rejected |
|--------|--------------|
| Vector-only | Misses exact-term queries; BM25 is complementary, not redundant |
| Neural cross-encoder (e.g. cross-encoder/ms-marco-MiniLM) | ML runtime dependency; GPU preferred for production latency; AP-3 risk |
| Elasticsearch / OpenSearch | Operational complexity; Postgres is already the data store |
| IVFFlat instead of HNSW | Requires pre-build list count; worse at low row counts |
