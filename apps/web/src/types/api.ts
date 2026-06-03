import { z } from "zod";

/** Liveness/readiness payload from /healthz and /readyz. */
export const HealthSchema = z.object({
  status: z.string(),
  service: z.string().optional(),
  version: z.string().optional(),
});
export type Health = z.infer<typeof HealthSchema>;

/**
 * A retrieval citation — the evidence behind every answer. Fields beyond source_id
 * are treated leniently since the backend may omit title/uri for some sources.
 */
export const CitationSchema = z.object({
  source_type: z.string(),
  source_id: z.string(),
  chunk_index: z.number().nullish(),
  content: z.string().default(""),
  score: z.number().nullish(),
  title: z.string().nullish(),
  source_uri: z.string().nullish(),
});
export type Citation = z.infer<typeof CitationSchema>;

/** Response from POST /retrieval/search. `has_citations` drives the trust banner. */
export const SearchResponseSchema = z.object({
  query: z.string(),
  has_citations: z.boolean(),
  citations: z.array(CitationSchema).default([]),
  retrieval_stages: z.record(z.string(), z.number()).default({}),
});
export type SearchResponse = z.infer<typeof SearchResponseSchema>;

export interface SearchRequest {
  query: string;
  top_k?: number;
  source_types?: Array<"document" | "note">;
}

// ── Ingest ────────────────────────────────────────────────────────────────
export type DocumentKind = "markdown" | "text" | "pdf";

/** Result of POST /documents. `deduplicated` true → identical content already stored. */
export const DocumentIngestResultSchema = z.object({
  id: z.string(),
  content_hash: z.string(),
  kind: z.string(),
  title: z.string().nullish(),
  source: z.string(),
  deduplicated: z.boolean(),
  ingested_at: z.string(),
});
export type DocumentIngestResult = z.infer<typeof DocumentIngestResultSchema>;

/** Result of POST /notes. */
export const NoteIngestResultSchema = z.object({
  id: z.string(),
  content_hash: z.string(),
  source: z.string(),
  deduplicated: z.boolean(),
  ingested_at: z.string(),
});
export type NoteIngestResult = z.infer<typeof NoteIngestResultSchema>;

export interface NoteIngestRequest {
  body: string;
  source: string;
  author?: string;
  tags?: string[];
}

// ── Compress ──────────────────────────────────────────────────────────────
/** Outcome of POST /compress/documents|notes/{id}. */
export const CompressResponseSchema = z.object({
  source_id: z.string(),
  source_type: z.string(),
  summaries_created: z.number(),
  has_mental_model: z.boolean(),
  has_playbook: z.boolean(),
});
export type CompressResponse = z.infer<typeof CompressResponseSchema>;

/** One summary level (brief/standard/detailed) from GET .../summaries. */
export const SummarySchema = z.object({
  id: z.string(),
  level: z.string(),
  word_count: z.number(),
  model_used: z.string(),
  content: z.string().default(""),
});
export type Summary = z.infer<typeof SummarySchema>;
export const SummaryListSchema = z.array(SummarySchema);

/** Structured mental model from GET .../mental-model. */
export const MentalModelSchema = z.object({
  id: z.string(),
  claims: z.array(z.string()).default([]),
  entities: z.array(z.record(z.string(), z.unknown())).default([]),
  relationships: z.array(z.record(z.string(), z.unknown())).default([]),
  has_playbook: z.boolean(),
  model_used: z.string(),
});
export type MentalModel = z.infer<typeof MentalModelSchema>;

/** Outcome of POST /retrieval/embed/documents|notes/{id}. */
export const EmbedResponseSchema = z.object({
  source_id: z.string(),
  source_type: z.string(),
  chunks_embedded: z.number(),
});
export type EmbedResponse = z.infer<typeof EmbedResponseSchema>;

// ── Execution ───────────────────────────────────────────────────────────────
/** Status values the backend accepts for goals and tasks (eci_execution.VALID_STATUSES). */
export const EXECUTION_STATUSES = [
  "pending",
  "in_progress",
  "completed",
  "blocked",
  "cancelled",
] as const;
export type ExecutionStatus = (typeof EXECUTION_STATUSES)[number];

/** A roadmap from POST/GET /roadmaps. */
export const RoadmapSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().nullish(),
});
export type Roadmap = z.infer<typeof RoadmapSchema>;
export const RoadmapListSchema = z.array(RoadmapSchema);

/** A goal from POST/GET/PATCH /goals. */
export const GoalSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().nullish(),
  status: z.string(),
  roadmap_id: z.string().nullish(),
  source_memory_id: z.string().nullish(),
});
export type Goal = z.infer<typeof GoalSchema>;
export const GoalListSchema = z.array(GoalSchema);

/** A task from POST/GET/PATCH /tasks. */
export const TaskSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().nullish(),
  status: z.string(),
  goal_id: z.string().nullish(),
  position: z.number(),
  source_memory_id: z.string().nullish(),
});
export type Task = z.infer<typeof TaskSchema>;
export const TaskListSchema = z.array(TaskSchema);

/** GET /goals|tasks/{id}/why — stored citations. Reuses the lenient CitationSchema
 *  (extra target_type/target_id fields are ignored). */
export const WhyListSchema = z.array(CitationSchema);

export interface CreateRoadmapInput {
  title: string;
  description?: string;
}

export interface CreateGoalInput {
  title: string;
  description?: string;
  roadmap_id?: string;
}

export interface CreateTaskInput {
  title: string;
  goal_id?: string;
  description?: string;
  position?: number;
}

export interface StatusUpdateInput {
  status: string;
  reason?: string;
}
