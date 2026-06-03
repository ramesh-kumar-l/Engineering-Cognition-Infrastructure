# Frontend Design — ECI Web (Premium, Provenance-First)

Status: **Phase C complete** (Execution). Phases A (scaffold + Search) and B (Ingest +
Compress) done. Source of truth for all frontend phases. The web app is an additive
`apps/web/` service that surfaces existing API provenance — it never re-derives evidence.
One small, approved backend change was required in Phase C (see Phase C notes).

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
- A: scaffold + Search vertical slice ✅
- B: Ingest + Compress ✅
- C: Execution (+ WhyDrawer) ✅
- D: Reflection ← next
- E: Observability & guidance polish + full validation

## Phase B notes (Ingest + Compress)
- `features/ingest/` — `DocumentForm` (multipart `POST /documents`), `NoteForm`
  (`POST /notes`), `IngestResult` (dedup badge + provenance + "Compress this →" handoff).
- `features/compress/` — id-driven screen: `Run compression` (`POST /compress/documents/{id}`),
  `SummaryList` (GET summaries), `MentalModelView` (GET mental-model; 404 = not built yet),
  `EmbedPanel` (`POST /retrieval/embed/documents/{id}` → "Go to Search").
- Handoff Ingest→Compress via typed search param `?documentId=` (`validateSearch` on route).
- New shared UI primitives: `ui/textarea`, `ui/select`, `ui/field`.
- **Env prerequisite**: Compress/Embed/Search query-embedding need an LLM provider. Ollama
  is NOT installed in this dev env → those endpoints return 5xx; the UI fails closed with a
  clear "LLM provider (Ollama) may be unavailable" message (matches risk R-002). Ingest is
  LLM-free and fully functional. To exercise the full loop: install Ollama + pull
  `nomic-embed-text` (embeddings) and a chat model, or set a cloud provider env var.
- Backend run with `ECI_IDENTITY_AUTH_DISABLED=true` (dev-bypass); no backend code changed.

## Phase C notes (Execution)
- `features/execution/` — master-detail across three columns: `RoadmapPanel` (create/select),
  `GoalPanel` (create/status/Why for the active roadmap), `TaskPanel` (create/status/upstream
  dependency/Why for the active goal). One `execution.api.ts` + one `use-execution.ts`.
- Shared provenance: `components/provenance/why-drawer.tsx` (Radix Dialog slide-over) renders
  `GET /goals|tasks/{id}/why` citations via the existing `CitationCard`. Fail-closed (AP-2):
  no stored evidence → explicit "unverifiable" amber notice.
- `StatusSelect` maps the backend's 5 valid statuses (pending/in_progress/completed/blocked/
  cancelled). Dependencies post `{upstream_id}`; 409 cycle errors surface inline.
- Endpoints used: `POST/GET /roadmaps`, `POST/GET /goals(?roadmap_id=)`, `PATCH /goals/{id}/status`,
  `GET /goals/{id}/why`, `POST/GET /tasks(?goal_id=)`, `PATCH /tasks/{id}/status`,
  `POST /tasks/{id}/dependencies`, `GET /tasks/{id}/why`. Execution is LLM-free → works without Ollama.
- **Approved backend change (the only one so far).** List endpoints scope by request-context
  `tenant_id`, but create paths wrote `tenant_id=NULL`, so lists returned `[]` for any tenant
  (prod bug, not just dev). Fix (user-approved): thread `ctx.tenant_id` into `create_roadmap/
  create_goal/create_task` (default `None` keeps existing service tests valid). The dev tenant
  `…0001` wasn't seeded, causing an FK violation, so added `apps/api/dev_seed.py` —
  idempotent seed of the dev tenant+user, run from the lifespan **only when auth is disabled**
  (no-op in production). New integration test: `test_create_roadmap_is_scoped_to_tenant`.
