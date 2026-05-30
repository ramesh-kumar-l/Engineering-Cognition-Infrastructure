# ADR-005 — LLM Runtime Abstraction

**Status:** Accepted
**Date:** 2026-05-30
**Phase:** Phase 3 — Knowledge Compression
**Supersedes:** —

## Context

Phase 3 introduces the first AI-generated content in ECI: summaries, mental models, and
playbooks derived from ingested documents and notes. This requires calling an LLM at runtime.
The charter prescribes:

- **AP-3** — Offline-first. Cloud-enhanced. Never cloud-dependent.
  Ollama must be the default; cloud providers are opt-in via configuration.
- **AP-6** — Long-term ownership. Avoid vendor lock-in.
  Switching providers must be a config change, not a code change.
- **R-001** — Cloud LLM availability and pricing volatility (open risk).

Three alternatives were considered:

1. **Vendor-specific calls inline** — simplest to write, hardest to swap.
   Violates AP-3 and AP-6 from day one.
2. **LangChain / LlamaIndex abstraction** — broad ecosystem, but opinionated and
   heavyweight. Fails AP-6 (lock-in to a framework, not just a vendor). History of
   breaking strict type checking.
3. **Thin Protocol interface with per-vendor adapters** — conforms to AP-5 (composable
   modules), AP-6 (swap any adapter without touching callers), AP-3 (Ollama ships with
   the package and requires only `httpx`; cloud adapters gate-import from optional deps).

## Decision

Adopt Option 3: a `packages/llm/` package (`eci-llm`) that exports:

- `LLMProvider` — a `Protocol` accepting `LLMRequest` and returning `LLMResponse`.
- `EmbeddingProvider` — a `Protocol` for synchronous embedding calls.
- `OllamaProvider` / `OllamaEmbeddingProvider` — the default offline adapters.
  Only required runtime dependency: `httpx`.
- `OpenAIProvider` / `OpenAIEmbeddingProvider` — optional; lazy-imported;
  raises `LLMProviderNotAvailable` with an install hint if the `openai` package is absent.
- `AnthropicProvider` — optional; same lazy-import guard.
- `OpenRouterProvider` — optional; reuses the `openai` SDK with a custom `base_url`.
- `create_llm_provider(config)` and `create_embedding_provider(config)` factory functions
  driven entirely by `LLMConfig` (env prefix `ECI_LLM_`).

Switching providers requires only an env-var change (`ECI_LLM_PROVIDER`), zero code edits.

## Embedding dimension convention

Default embedding dimension is **768** (Ollama `nomic-embed-text`).
OpenAI `text-embedding-3-small` is 1536.
`LLMConfig.embedding_dim` must match the model in use.
A mismatch will fail at the pgvector index creation step (Phase 4) with a clear error.

Phase 4 will consume `EmbeddingProvider`; storage of embeddings is deferred to that phase.

## Consequences

**Good:**
- AP-3 met: Ollama is the default; `httpx` is the only required runtime dep.
- AP-6 met: callers depend only on `LLMProvider` / `EmbeddingProvider` Protocols.
- `mypy --strict` passes: Protocols are `runtime_checkable`; no `Any` in the public surface.
- Cloud packages (`openai`, `anthropic`) are optional extras; never imported at module load.

**Accepted costs:**
- Thin adapters must track vendor API changes independently.
- OpenRouter reuses the OpenAI SDK (known coupling, documented here).
- No async — all providers are synchronous. Async wrapping is a P8 optimization.

## Related

- R-001 (cloud LLM availability), R-002 (Ollama hardware requirements).
- Phase 4 ADR (retrieval) will consume `EmbeddingProvider` as its embedding seam.
