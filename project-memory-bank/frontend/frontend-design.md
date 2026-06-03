# Frontend Design — ECI Web (Premium, Provenance-First)

Status: **Phase A in progress** (scaffold + Search vertical slice). Source of truth for
all frontend phases. Backend is GA-ready and unchanged; the web app is an additive
`apps/web/` service that surfaces existing API provenance — it never re-derives evidence.

## Principles (inherited from system-patterns.md)
- **Evidence before inference (AP-2)** → provenance is always visible; fail-closed UI
  when `has_citations=false`.
- **Human in control (AP-4)** → users can inspect "why", audit status changes, override.
- **Offline-first (AP-3)** → no third-party UI runtime services; works against local API.
- **Modularity** → hard 300-line file cap, one responsibility per file (same as backend).

## Product spine (navigation = the cognition loop)
`Overview → Ingest → Compress → Search → Execution → Reflection → Observability`
Left rail follows the loop; top bar carries global search, tenant/actor context, and a
live health pill. The order teaches the workflow.

## Screen → endpoint map
| Screen | Primary endpoints |
|---|---|
| Overview | `GET /healthz` `/readyz` `/metrics`; counts via list endpoints; links to `/docs` |
| Ingest | `POST /documents` (multipart), `POST /notes` |
| Compress | `POST /compress/documents/{id}`; `GET /compress/documents/{id}/summaries`, `/mental-model`; `POST /retrieval/embed/documents/{id}` |
| Search | `POST /retrieval/search` → `{ has_citations, citations[], retrieval_stages }` |
| Execution | `POST/GET /roadmaps`, `/goals`, `/tasks`; `PATCH /goals\|tasks/{id}/status`; `POST /tasks/{id}/dependencies`; `GET /goals\|tasks/{id}/why` |
| Reflection | `POST/GET /retrospectives`; `POST/GET /lessons`; `POST /lessons/{id}/supersede` |
| Observability | `/healthz` `/readyz` `/metrics`; SLO targets from `slos/slos.md`; deep links to Swagger/ReDoc/Grafana |

## Provenance contract (shared, reused everywhere)
- `CitationCard` — title, `source_uri`, `score`, chunk `content`, `source_type`.
- `HasCitationsBanner` — green "evidence-backed" when `has_citations`; red
  "no sources — unverifiable" otherwise.
- `WhyDrawer` — renders `GET /goals|tasks/{id}/why` stored citations (Phase C).
- `EvidenceList` — lesson `evidence[]` with summaries (Phase D).
- `retrieval_stages` chip — bm25 vs semantic contribution.

## Data flow
Typed `fetch` client (base `/api`) → TanStack Query (cache/loading/error) → feature
hooks (`useSearch`, …) → screens. Auth/tenant context injects Bearer + `X` headers
centrally; 401 surfaces an auth prompt. Dev: Vite proxies `/api/*` → `http://localhost:8000`
(no CORS). Prod: set `ECI_CORS_ORIGINS`. Auth starts in dev-bypass mode
(`ECI_IDENTITY_AUTH_DISABLED=true`); OIDC `/auth/login`+`/auth/callback` drop in later.

## Stack (ADR-002 + confirmed)
React 18 · TypeScript 5 strict · Vite · Tailwind v4 + Radix primitives (shadcn-style
local components) · TanStack Query + TanStack Router · Zod · Vitest + Testing Library.

## Phase status
- A: scaffold + Search vertical slice ← current
- B: Ingest + Compress
- C: Execution (+ WhyDrawer)
- D: Reflection
- E: Observability & guidance polish + full validation
