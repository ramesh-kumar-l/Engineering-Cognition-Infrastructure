# ADR-011 — Grounded LLM Assistant + Source Read Surface

- **Status:** Accepted
- **Date:** 2026-06-06
- **Deciders:** Project lead
- **Phase:** Post-GA (frontend vertical completion)

## Context

The product spine is **Ingest → Search → Document Viewer → LLM Assistant**. The first
two are live, but two pieces of the named vertical have no backend support:

1. **Document Viewer.** The UI can ingest and search, but there is no way to read a
   single source. The ingest routers expose only `POST /documents` and `POST /notes`;
   there is **no read-by-id or list endpoint**. The data already exists
   (`eci_storage.models.Document` / `Note` carry `body`, metadata, `tenant_id`).

2. **LLM Assistant.** ECI deliberately has **no generative endpoint** —
   `/retrieval/search` returns citations only, honouring AP-2 (*evidence before
   inference*). A conversational assistant needs a retrieval-augmented endpoint that
   synthesises an answer **strictly from retrieved citations**. The `LLMProvider`
   Protocol (`packages/llm/.../protocol.py`) is synchronous and has **no streaming**
   method; `OllamaProvider` hardcodes `"stream": False`.

## Decision

### 1. Source read endpoints

Add read-only, tenant-scoped endpoints, mirroring the auth/tenant pattern already used
by `/retrieval/search` (`ctx.tenant_id` from `get_request_context`):

| Endpoint | Returns |
|---|---|
| `GET /documents` | Paginated list: id, kind, title, source, tags, ingested_at |
| `GET /documents/{id}` | Full document incl. `body`, metadata, content_hash |
| `GET /notes/{id}` | Full note (search citations resolve to documents *and* notes) |

Reads live in a new `eci_ingest/read_service.py` (`SourceReadService`) consumed via DI
providers in `apps/api/.../dependencies.py`; router files stay thin. Tenant isolation is
enforced in the service: a row whose `tenant_id` differs from the caller's is treated as
not found (404), never leaked.

### 2. Grounded assistant endpoints

New router `apps/api/.../routers/assistant.py` backed by an `AssistantService` that
**reuses `packages/retrieval`** (it already owns `HybridRetriever` and the citation
model — no new workspace package):

- `POST /assistant/ask` → JSON `{answer, has_citations, citations[]}`.
- `POST /assistant/stream` → `text/event-stream`: token frames, then a terminal
  `event: citations` frame.

**Fail-closed (AP-2) is the core invariant.** Both endpoints retrieve first; if
retrieval yields **zero citations**, the service returns `has_citations=false` with a
null answer and **never calls the LLM**. When citations exist, the prompt instructs the
model to answer *only* from the numbered context, cite `[n]`, and say so when the context
is insufficient. This makes citation coverage a structural property, not a hope.

### 3. Additive streaming capability (non-breaking)

The shared `LLMProvider` Protocol is consumed by compression and reflection; changing its
required surface would ripple. Instead we add a **separate** `runtime_checkable`
`StreamingLLMProvider` Protocol with `stream_complete(LLMRequest) -> Iterator[str]`, and
implement it on `OllamaProvider` (real NDJSON streaming via `"stream": True` on
`/api/chat`). `AssistantService` uses `isinstance(provider, StreamingLLMProvider)` and
falls back to a single-chunk yield of `complete()` for providers that don't implement it.
Offline-first (AP-3) is preserved: Ollama is the default and streams natively.

## Consequences

**Positive.**
- The Document Viewer and Assistant vertical can be completed in the UI.
- Citation coverage on generated answers is enforced at the service boundary (SLO-4).
- Streaming is a capability, not a breaking protocol change — cloud providers opt in later.

**Negative.**
- Cloud LLM providers (OpenAI/Anthropic/OpenRouter) stream as a single chunk until they
  implement `stream_complete`. Acceptable: Ollama is the offline default.
- SSE adds a streaming response path; covered by the assistant unit + integration tests.

**Neutral.**
- No schema/migration change — all reads use existing tables and columns.

## Alternatives Considered

- **New `packages/assistant` workspace package** — rejected: the assistant is retrieval +
  one prompt; it belongs with `packages/retrieval`, which already owns citations.
- **Add `stream_complete` to the existing `LLMProvider` Protocol** — rejected: forces
  compression/reflection-facing providers to implement streaming they don't need.
- **Synthesise even with zero citations, flagged "unverified"** — rejected: violates AP-2.
  Fail closed instead.
