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
