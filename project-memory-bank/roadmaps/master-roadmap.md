# ECI Master Roadmap — Phase 1 through Phase 8

## Context

The ECI charter (the user's "MASTER ARCHITECT SYSTEM PROMPT") is ratified. The repository currently contains only `LICENSE` and a one-line `README.md` on `develop`. There is no memory bank, no ADRs, no scaffolding.

This plan is the content that will later be persisted to `project-memory-bank/roadmaps/master-roadmap.md` during Phase 1 execution. It is **not** a plan to write code. It is the roadmap artifact itself, derived from the charter, structured to give every subsequent phase a concrete, verifiable exit.

Why this matters: the charter prescribes architecture, principles, and the eight-phase order, but does not define per-phase **exit criteria** or **dependencies**. Without those, RULE 4 ("single phase execution") cannot be enforced — there is no objective signal that a phase is done. This roadmap fixes that.

Charter rules this roadmap is bound by:
- **RULE 1** — Memory bank first. The roadmap lives in the memory bank and is read before any phase begins.
- **RULE 3** — No destructive change. Later phases build on earlier ones; they do not rewrite them.
- **RULE 4** — One phase at a time. Each phase has a single explicit exit gate.
- **RULE 5** — Architecture before code. Every phase carries an ADR commitment.
- **RULE 6** — Trust over magic. Every feature passes the five-question trustworthiness check.

---

## Cross-cutting commitments (apply to every phase)

These are not phase work — they are the rails every phase runs on.

1. **ADR discipline.** Any architecturally meaningful decision (storage, runtime, retrieval, auth, deployment) is recorded as an ADR in `project-memory-bank/architecture-decisions/` **before** code is written. ADR-001 ratifies the charter itself; ADR-002 ratifies the technology stack.
2. **Six quality gates per phase.** Architecture, Security, Testing, Observability, Documentation, Performance. A phase cannot exit until all six are signed off in that phase's completion report.
3. **Trustworthiness checklist per user-facing feature.** Verifiable, auditable, overridable, traceable, explainable. Recorded in the phase's memory-bank update.
4. **Memory bank updates close every phase.** `active-context.md` advances to the next phase, `progress.md` records completed work + lessons, `system-patterns.md` records any new patterns, `risk-register/risks.md` records any new risks.
5. **AP-3 enforced from Phase 1.** Offline-first. No phase introduces a cloud-dependent code path without an offline fallback.
6. **Evaluation-driven development from Phase 3 onward.** Any phase that ships AI behavior also ships an entry in `evaluations/` with the metric + threshold used to accept that behavior.

---

## Phase dependency graph

```
P1 (Foundation)
  └─> P2 (Capture)
        └─> P3 (Compression) ──┐
              └─> P4 (Memory) ─┴─> P5 (Execution)
                                    └─> P6 (Reflection)
                                          └─> P7 (Enterprise)
                                                └─> P8 (Production Hardening)
```

Each arrow is a hard dependency — the downstream phase cannot begin until the upstream phase's exit criteria are met and recorded in `progress.md`.

---

## Phase 1 — Foundation

**Objective.** Make the repository governable. Stand up the memory bank, the ADR pipeline, the observability spine, and the CI skeleton so that every later phase has a substrate to plug into.

**In scope.**
- Repository skeleton (monorepo layout: `apps/`, `packages/`, `infra/`, `docs/`, `project-memory-bank/`).
- The six core memory-bank files (`projectbrief.md`, `product-context.md`, `system-patterns.md`, `tech-context.md`, `active-context.md`, `progress.md`) populated with first-pass content drawn from the charter.
- Memory-bank subdirectories created: `architecture-decisions/`, `research/`, `evaluations/`, `roadmaps/`, `risk-register/`.
- **ADR-001** — Charter ratification (this charter, immutable).
- **ADR-002** — Technology stack ratification (React + TS + Tauri / FastAPI + Pydantic / Postgres + pgvector / Ollama+OpenAI+Anthropic+OpenRouter / Langfuse + OTel + Prometheus + Grafana / MkDocs / Docker + K8s).
- **ADR-003** — Repo and branching layout.
- Observability baseline: one OTel trace travels end-to-end through a placeholder request handler; Langfuse + Prometheus wiring stubbed and reachable.
- CI skeleton (lint, type-check, unit-test runners over empty packages — must go green).
- MkDocs site initialized; renders the memory bank.

**Deferred.** No product code, no ingestion, no retrieval, no UI beyond a "hello" route.

**Dependencies.** None.

**Exit criteria.**
- All six memory-bank files exist, are non-empty, and pass `mkdocs build` without warnings.
- ADR-001, ADR-002, ADR-003 are ratified (status: Accepted) and linked from `system-patterns.md`.
- A `make smoke` (or equivalent) target produces one trace visible in Langfuse, one metric in Prometheus, one log in the configured sink.
- CI is green on `main` and on a throwaway feature branch.
- `active-context.md` reads: current phase = Phase 2; blockers = none.

**Quality gates.** Architecture (charter + stack ADRs), Observability (baseline live), Documentation (memory bank renders), Testing (CI green), Security (no secrets in repo, dependabot/equivalent on), Performance (n/a — recorded as deferred).

**Memory bank updates.** Initial population of all six files. `progress.md` records Phase 1 complete. `risks.md` initialized with at least the cloud-LLM availability risk and the offline-Ollama hardware risk.

---

## Phase 2 — Knowledge Capture

**Objective.** Get real data into ECI: documents, notes, and their metadata, with provenance preserved.

**In scope.**
- Ingestion API for documents (markdown, PDF, plain text) and notes (short-form, hand-authored).
- Metadata model (source, author, captured_at, content_hash, tags, provenance chain).
- Raw storage (object/blob layer for source files) + parsed storage (Postgres tables for normalized content + metadata).
- Idempotent ingestion (content_hash collision → no-op).
- ADR for storage layout (raw vs. parsed separation, retention).

**Deferred.** Summarization, embeddings, retrieval, UI beyond an ingestion endpoint.

**Dependencies.** Phase 1.

**Exit criteria.**
- A markdown document and a short note can each be ingested via API; both round-trip retrievable by ID with full provenance.
- Re-ingesting the same content produces zero duplicate rows.
- Ingestion emits a trace per request and a Prometheus counter per source type.
- Integration tests run against a real Postgres (not mocks), per the global "no mocked DB" preference.
- `evaluations/` contains a placeholder file describing the ingestion correctness check (will be expanded in P3+).

**Quality gates.** Architecture (storage ADR), Security (input validation, file-type allowlist, size limits), Testing (real-DB integration tests pass), Observability (per-ingest trace + metric), Documentation (API documented in MkDocs), Performance (ingest a 10MB doc in < N seconds — threshold set during phase).

**Memory bank updates.** `system-patterns.md` gains the ingestion + provenance pattern. `progress.md` records P2 complete. `active-context.md` advances to P3.

---

## Phase 3 — Knowledge Compression

**Objective.** Turn raw captured content into compressed, queryable representations — summaries, mental models, playbooks — through a swappable LLM runtime.

**In scope.**
- LLM runtime abstraction: a single interface backed by Ollama (offline default), OpenAI, Anthropic, OpenRouter. Selection via config, no hard-coded vendor.
- Multi-level summarization pipeline (short / medium / long; per-doc + per-collection).
- Mental-model extraction (key claims, entities, relationships) stored as structured records linked to source.
- Playbook templates (reusable, parameterized recipes for compression).
- Evaluation harness for summarization quality (faithfulness, coverage, latency) recorded under `evaluations/rag-metrics.md` precursor.

**Deferred.** Retrieval (P4), citations at query time (P4), goal/task extraction (P5).

**Dependencies.** Phase 2 (need ingested content).

**Exit criteria.**
- Switching LLM provider requires only a config change; no code edits.
- Every ingested document produces at least one summary at each level and a structured mental-model record.
- Offline path (Ollama) produces complete output for the integration test corpus without network.
- Summary faithfulness score (vs. source) meets the threshold recorded in `evaluations/`. Threshold is set during the phase; it must be set before exit.
- AP-2 enforced: every compressed artifact carries a pointer back to its source records.

**Quality gates.** Architecture (LLM-runtime ADR), Security (prompt-injection defense at boundary, no exfil of source via prompt), Testing (golden-set eval), Observability (Langfuse traces per LLM call), Documentation (runtime + playbook docs), Performance (latency thresholds met for Ollama and at least one cloud provider).

**Memory bank updates.** `system-patterns.md` gains the LLM-runtime abstraction and compression patterns. `evaluations/` gains the first real benchmark file.

---

## Phase 4 — Engineering Memory

**Objective.** Production-grade retrieval with evidence. This is the phase that delivers AP-1 ("memory is the product") and AP-2 ("evidence before inference") as a working product surface.

**In scope.**
- Hybrid retrieval: BM25 (Postgres FTS) + vector (pgvector) + cross-encoder rerank.
- Citation engine: every answer carries source citations resolvable to the original ingested record.
- Long-term memory store: distinct from raw ingest — curated, embeddings-indexed, versioned.
- Retrieval benchmark suite (`evaluations/retrieval-benchmarks.md`) with held-out queries and accepted thresholds (recall@k, MRR, citation coverage).
- "No answer without provenance" enforced at the API layer.

**Deferred.** Execution intelligence (P5). Multi-tenancy (P7).

**Dependencies.** Phase 2 (data), Phase 3 (embeddings / compressed forms).

**Exit criteria.**
- Retrieval benchmarks meet the accepted thresholds on the held-out set.
- 100% of generated answers in the integration test suite carry at least one resolvable citation; answers without citations fail closed.
- Trustworthiness checklist passes for the answer surface: verifiable (citations), auditable (logged), overridable (manual edit), traceable (source links), explainable (reasoning summary attached).
- Index rebuild from raw ingest is reproducible and documented.

**Quality gates.** Architecture (retrieval ADR), Security (per-source access control hooks reserved for P7), Testing (benchmark suite green), Observability (per-query trace with retrieval stages broken out), Documentation (citation contract documented), Performance (query latency p95 threshold met).

**Memory bank updates.** `evaluations/retrieval-benchmarks.md` becomes the source of truth for retrieval acceptance. `system-patterns.md` records the hybrid retrieval pattern.

---

## Phase 5 — Execution Intelligence

**Objective.** Turn memory into action. Goals, tasks, and roadmaps that trace back to the memory that justifies them.

**In scope.**
- Domain models for Goal, Task, Roadmap with dependency edges and status.
- Linkage from every execution item back to the source memory (decision, document, or lesson) that motivated it.
- Status-change audit log (who, when, why, prior state).
- Read APIs for "why does this task exist?" — must return source citations from P4.

**Deferred.** Multi-user permissions (P7). Reflection / learning (P6).

**Dependencies.** Phase 4.

**Exit criteria.**
- A Goal can be created from a memory query result and inherits the citation chain.
- "Why does this task exist?" returns a non-empty, source-cited justification for every task in the integration corpus.
- All status changes are audited with prior + new state.
- Trustworthiness checklist passes for the execution surface.

**Quality gates.** Architecture (execution-model ADR), Security (write-path auth hook reserved for P7, but write paths already audited), Testing (audit-log invariant tests), Observability (per-write trace), Documentation, Performance.

**Memory bank updates.** `system-patterns.md` gains the execution + provenance-link pattern. `progress.md` records P5 complete.

---

## Phase 6 — Reflection Engine

**Objective.** Compound learning. Periodic retrospectives that turn execution history + outcomes into stored lessons, with sources.

**In scope.**
- Retrospective generator (configurable cadence: weekly, monthly, per-milestone).
- Pattern extraction across goals/tasks/outcomes.
- Lesson register (a typed memory record with: claim, evidence, scope, confidence, supersedes).
- Reflection runs are themselves audited and citable.

**Deferred.** Multi-team rollups (P7).

**Dependencies.** Phase 5 (needs execution history to reflect on).

**Exit criteria.**
- A scheduled reflection run produces at least one lesson record per cycle on the integration corpus.
- Every lesson cites the execution events and source memories it derives from.
- A lesson can supersede a prior lesson; supersession is auditable.
- Reflection-quality eval (does the lesson actually match the evidence?) recorded in `evaluations/` with threshold met.

**Quality gates.** Architecture (lesson-record ADR), Evaluation (reflection-quality benchmark), Trustworthiness (lessons are explainable + source-cited), plus the standard six.

**Memory bank updates.** First real entries in a lessons store. `system-patterns.md` gains the reflection pattern.

---

## Phase 7 — Enterprise

**Objective.** Make ECI multi-user and multi-tenant without breaking trust.

**In scope.**
- RBAC at the API boundary; role definitions documented as an ADR.
- Audit trail across all write paths (ingestion, execution, reflection).
- Team workspaces with isolation guarantees verified by tests.
- SSO hooks (OIDC) — at least one provider wired end-to-end.
- Per-source access control on retrieval results (citations are filtered, not just hidden).

**Deferred.** Production hardening (P8). Billing / quotas.

**Dependencies.** Phases 1–6 stable; benchmarks still green.

**Exit criteria.**
- A user in team A cannot read team B's data via any read path (verified by negative tests).
- Every write path produces an audit record with actor identity.
- RBAC denies are observable (metric + log) and explainable to the user.
- Trustworthiness checklist passes for the enterprise surface.

**Quality gates.** Security (full review — this is the dedicated security phase), Architecture (tenancy + RBAC ADRs), Testing (multi-tenant isolation tests), Observability, Documentation, Performance (no regression vs. P6 baselines).

**Memory bank updates.** Tenancy + RBAC patterns recorded. New risks recorded (data leakage, privilege escalation) with mitigations cross-linked to ADRs.

---

## Phase 8 — Production Hardening

**Objective.** GA readiness. All six gates pass continuously, not just at phase exit.

**In scope.**
- CI/CD pipelines for build, test, eval, deploy (staging → prod) with required reviewers.
- Security: dependency scanning, SAST, secret scanning, base-image policy, regular pen-test cadence.
- Continuous evaluation: P3, P4, P6 benchmarks run on every release candidate; release blocked on regression.
- SLOs defined and measured (availability, latency p95/p99, citation coverage, retrieval recall).
- Disaster recovery: documented runbook + executed DR drill (restore from backup, verify integrity).
- Observability matured: dashboards for SLOs, alerts wired to a real channel.

**Deferred.** Nothing — this is the terminal phase. Anything not done here is a known gap recorded in `risk-register/risks.md`.

**Dependencies.** Phase 7.

**Exit criteria.**
- SLOs defined in writing and measured in Grafana for at least one full week.
- DR drill executed end-to-end; recovery time + data-loss window recorded and within target.
- Eval suite runs on every PR; one demonstrated release-blocking regression caught.
- Security review complete with findings tracked to closure (open findings explicitly accepted with owner + date).
- All six quality gates pass on the release-candidate build with evidence linked.

**Quality gates.** All six, with evidence, on the release candidate.

**Memory bank updates.** `progress.md` records GA. `system-patterns.md` records the release pattern. `risks.md` reconciled (closed vs. accepted).

---

## Decisions deferred (not made by this roadmap)

These are explicitly **not** decided here. Each will become an ADR in the phase that owns it.

- Specific Postgres version + pgvector version (P1 ADR-002 candidate).
- Embedding model family and dimension (P3).
- Cross-encoder reranker choice (P4).
- Auth provider for SSO in P7.
- Deployment target order: Tauri desktop first vs. K8s server first (P1 follow-up ADR).
- Specific eval thresholds for P3/P4/P6 — set during their phases, not pre-committed here.
- Vendor LLM cost ceiling and fallback policy when offline is unavailable.

Pre-committing any of these would violate "simplicity first" and "architecture before code" — the ADR for each belongs to the phase that consumes it.

---

## Verification — how we know the roadmap is being followed

Read-only checks that any reviewer (human or agent) can run against the repo at any time:

1. `project-memory-bank/active-context.md` names exactly one current phase, and that phase's predecessors are marked complete in `progress.md`.
2. Every accepted ADR in `architecture-decisions/` is referenced from at least one memory-bank file or one phase completion report.
3. For each completed phase N, `evaluations/` contains the benchmark file(s) that phase committed to, with thresholds recorded.
4. `risk-register/risks.md` has entries dated within the current phase's window — risks are reviewed, not just appended.
5. CI is green on `main`; the most recent release candidate (if any) has evidence for all six quality gates linked.
6. No code path exists that violates AP-3 (offline-first) without a written ADR exception.

---

## Critical files this plan implies (to be created during Phase 1, not now)

- `project-memory-bank/roadmaps/master-roadmap.md` — receives the body of this plan.
- `project-memory-bank/projectbrief.md`, `product-context.md`, `system-patterns.md`, `tech-context.md`, `active-context.md`, `progress.md` — initial content from the charter.
- `project-memory-bank/architecture-decisions/ADR-001-charter-ratification.md`, `ADR-002-technology-stack.md`, `ADR-003-repo-and-branching.md`.
- `project-memory-bank/risk-register/risks.md`.
- `project-memory-bank/evaluations/` — empty, with a `README.md` describing the contract for future benchmark files.

Nothing else is created by this roadmap. Phase 1 will be its own approved scope.
