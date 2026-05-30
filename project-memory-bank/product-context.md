# Product Context

## Primary Users
- **Individual senior engineers / staff+ engineers** who accumulate knowledge across multi-year projects and lose context to attrition (job changes, team moves, time).
- **Engineering teams** who need shared institutional memory that survives turnover.
- **Architects / tech leads** who need to defend or revisit past decisions with evidence, not memory.

## Pain Points
1. **Decision provenance is lost.** Why we chose X over Y is in a 2-year-old Slack thread that no longer exists.
2. **Knowledge does not compound.** Lessons learned from incidents, postmortems, and design reviews are re-learned every cycle.
3. **Context decay.** Returning to a project after months means rebuilding mental model from scratch.
4. **Tool sprawl.** Notion, Confluence, Slack, GitHub, Linear, Jira — knowledge is fragmented, none is the source of truth.
5. **AI tools hallucinate.** Current LLM assistants invent answers without sources, eroding trust.

## Jobs To Be Done
- *Help me remember what I learned about [topic] across all my past work.*
- *Help me defend this architecture decision with the evidence we had at the time.*
- *Help me see the patterns in our incident history without re-reading every postmortem.*
- *Help me onboard onto a project I last touched 18 months ago.*
- *Help me decide what to work on next, given my goals and accumulated lessons.*

## Success Metrics (north stars)
| Metric | Target horizon |
|---|---|
| Citation coverage on generated answers | 100% (fail closed at the API layer) — by end of P4 |
| Retrieval recall@10 on held-out benchmark | Threshold set in P4, met continuously thereafter |
| Lesson reuse rate (lessons referenced by later decisions) | Tracked from P6 onward |
| Mean time to first useful answer for a new ingest | Tracked from P2 onward |
| Time-to-recover from cold start (DR drill) | Within target, P8 |

## Anti-Goals
- Maximize generated text volume.
- Replace human judgment.
- Become another knowledge-base UI to maintain.
- Lock users into a single LLM, embedding model, or cloud provider.

## Trustworthiness Contract (applied to every user-facing feature)
A feature is production-ready only if a user can:
1. **Verify** its output against cited sources.
2. **Audit** what the system did and when.
3. **Override** the output.
4. **Trace** the output back to inputs.
5. **Understand** why it produced what it did.

See ADR-001 for ratification.
