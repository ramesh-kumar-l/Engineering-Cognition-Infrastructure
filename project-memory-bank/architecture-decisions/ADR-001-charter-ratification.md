# ADR-001 — Charter Ratification

- **Status:** Accepted
- **Date:** 2026-05-30
- **Deciders:** Project lead
- **Phase:** P1

## Context
The ECI "Master Architect" system prompt (the charter) defines product mission, non-negotiable operating rules (RULE 1–6), architectural principles (AP-1–AP-6), the preferred technology stack, the memory-bank structure, the phase execution framework, and the trustworthiness contract. Without explicit ratification, the charter's authority is ambiguous and downstream phases could drift.

## Decision
The charter is **ratified as the immutable governing document** for ECI. All phases, ADRs, and code are bound by it. The charter text is preserved verbatim and is **not edited** as part of normal work; amendments require a successor ADR that explicitly supersedes this one.

Specifically:
1. RULES 1–6 are binding on every contributor (human or agent).
2. AP-1 through AP-6 are binding architectural principles, evaluated in every code review.
3. The eight-phase order (P1 → P8) is binding; phases are executed one at a time.
4. The six quality gates (Architecture, Security, Testing, Observability, Documentation, Performance) are required exits for every phase.
5. The trustworthiness contract (verifiable, auditable, overridable, traceable, explainable) is required for every user-facing feature.

## Consequences
**Positive.**
- Single source of authority for product direction. Phase plans and ADRs reference the charter.
- Reduces re-litigation of foundational decisions.
- Makes "is this in scope?" a tractable question.

**Negative.**
- The charter is opinionated; some valid alternatives are foreclosed (e.g., autonomous agent patterns). Accepted trade-off.
- Charter amendments are deliberately friction-heavy (require a superseding ADR). This is intentional.

**Neutral.**
- The memory bank is now the operational interface to the charter (RULE 1).

## Alternatives Considered
- **Treat the charter as draft and iterate.** Rejected: this is exactly the source of multi-quarter drift in similar projects. Long-term ownership (AP-6) requires a stable foundation.
- **Pick only some rules.** Rejected: the rules are interdependent (e.g., RULE 4 single-phase execution depends on RULE 5 architecture-before-code).

## Compliance
A reviewer can verify by:
1. Confirming `project-memory-bank/active-context.md` names exactly one current phase.
2. Confirming every architecturally meaningful change has an ADR before code.
3. Confirming every phase completion report records all six quality gates.
4. Confirming user-facing features carry the trustworthiness checklist in their phase's memory-bank update.
