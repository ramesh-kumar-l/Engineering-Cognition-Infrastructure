# Project Brief

## Vision
A trustworthy engineering memory that compounds over years — the system of record for engineering knowledge, decisions, lessons, and execution.

## Mission
Operate the loop: **Capture → Understand → Compress → Connect → Remember → Retrieve → Execute → Reflect → Improve** — with source traceability at every step.

## Primary Objective
Build a product engineers trust. In priority order:
1. **Correctness** over speed.
2. **Trustworthiness** over intelligence.
3. **Reliability** over novelty.
4. **Evidence** over confidence.

## Goals
- Every generated answer cites resolvable sources.
- Every architecturally meaningful decision is recorded as an ADR before code is written.
- Offline-first: no cloud-dependent code path without an offline fallback.
- Long-term ownership: avoid vendor lock-in at the runtime, storage, and observability layers.

## In Scope
- Knowledge capture from documents, notes, and structured artifacts.
- Compression into summaries, mental models, playbooks.
- Hybrid retrieval (BM25 + vector + cross-encoder rerank) with citations.
- Goals/tasks/roadmaps linked to source memory.
- Periodic reflection that produces typed lessons.
- Multi-user, multi-tenant readiness.
- Production SLOs, DR, evaluation-gated releases.

## Out of Scope (current cycle)
- Autonomous agents that act without human approval.
- Self-modifying memory or hidden state mutation.
- Vendor lock-in to a single LLM or cloud provider.
- Real-time collaboration (deferred until post-GA).

## Definition of Success
An engineer can ask:
- *Why was this decision made?*
- *What did I learn about distributed systems last year?*
- *What patterns repeatedly caused failures?*
- *What should I focus on next?*

…and receive evidence-backed, source-cited, reproducible answers.

## Links
- [Master roadmap](roadmaps/master-roadmap.md)
- [Architecture decisions](architecture-decisions/)
- [Active context](active-context.md)
