# Active Context

> **Read this first.** This file is the current "save state" of the project. It is updated at the end of every major feature and at every phase transition.

## Current Phase
**Phase 1 — Foundation** *(in progress at file creation; will flip to Phase 2 once Phase 1 exit criteria are met — see [implementation-status.md](implementation-status.md))*

## Current Sprint Goal
Stand up the substrate: memory bank populated, ADR-001/002/003 ratified, observability spine reachable, CI green, MkDocs renders the bank.

## Active Work
- Memory bank initial population ✅
- ADRs ratified ✅
- Repo skeleton (apps/, packages/, infra/, docs/) ✅
- Observability package wired (OTel + Prometheus + structlog + Langfuse stub) ✅
- API stub consumes observability ✅
- `make smoke` proves wiring ✅
- CI workflow committed (executes once pushed to a remote) ✅

## Open Decisions
*(decisions surfaced but not yet recorded as ADRs)*
- **Deployment target order.** Tauri desktop vs. K8s server first. Not decided in P1; revisit before P4 UI work.
- **Cross-encoder reranker choice.** Defer to P4 ADR.
- **Embedding model family.** Defer to P3 ADR.

## Blockers
None.

## Risks Currently Top-of-Mind
See [risk-register/risks.md](risk-register/risks.md). Highest current:
- **R-001** Cloud LLM availability (mitigated by Ollama offline path — partial).
- **R-002** Offline-Ollama hardware requirements (no mitigation yet — research in P3).

## Recently Updated
- **2026-05-30** Phase 1 scaffolding committed. ADR-001/002/003 ratified. Observability spine reachable via console exporters. Phase 2 unblocked.

## Next Phase
**Phase 2 — Knowledge Capture.** Do not begin until Phase 1 exit criteria are confirmed in [implementation-status.md](implementation-status.md). Charter RULE 4 — one phase at a time.
