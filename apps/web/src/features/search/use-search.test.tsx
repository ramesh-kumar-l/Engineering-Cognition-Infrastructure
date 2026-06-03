import { describe, it, expect, vi } from "vitest";
import type { ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useSearch } from "./use-search";

function wrapper() {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

const RESPONSE = {
  query: "hybrid retrieval",
  has_citations: true,
  citations: [
    {
      source_type: "document",
      source_id: "11111111-2222-3333-4444-555555555555",
      chunk_index: 5,
      content: "Hybrid retrieval combines BM25 with vector search.",
      score: 0.89,
      title: "ADR-006",
      source_uri: "repo://adr-006",
    },
  ],
  retrieval_stages: { bm25: 25, semantic: 15 },
};

describe("useSearch", () => {
  it("posts the query and returns validated, cited results", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => RESPONSE,
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useSearch(), { wrapper: wrapper() });
    result.current.mutate({ query: "hybrid retrieval" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(fetchMock).toHaveBeenCalledWith("/api/retrieval/search", expect.objectContaining({ method: "POST" }));
    expect(result.current.data?.has_citations).toBe(true);
    expect(result.current.data?.citations[0].title).toBe("ADR-006");
    expect(result.current.data?.retrieval_stages.bm25).toBe(25);
  });
});
