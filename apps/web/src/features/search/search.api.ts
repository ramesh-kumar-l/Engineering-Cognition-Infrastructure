import { apiRequest } from "@/lib/api-client";
import { SearchResponseSchema, type SearchRequest, type SearchResponse } from "@/types/api";

/** Hybrid keyword + semantic search. Response always carries explicit citations. */
export function searchMemory(req: SearchRequest): Promise<SearchResponse> {
  return apiRequest("/retrieval/search", {
    method: "POST",
    body: {
      query: req.query,
      top_k: req.top_k ?? 10,
      source_types: req.source_types ?? ["document", "note"],
    },
    schema: SearchResponseSchema,
  });
}
