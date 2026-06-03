import { describe, it, expect, vi } from "vitest";
import type { ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useCompressDocument, useDocumentSummaries } from "./use-compress";

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

describe("useCompressDocument", () => {
  it("posts to /compress/documents/{id} and returns the outcome", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        source_id: "d-1",
        source_type: "document",
        summaries_created: 3,
        has_mental_model: true,
        has_playbook: false,
      }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useCompressDocument(), { wrapper: wrapper() });
    result.current.mutate("d-1");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/compress/documents/d-1",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.current.data?.summaries_created).toBe(3);
    expect(result.current.data?.has_mental_model).toBe(true);
  });
});

describe("useDocumentSummaries", () => {
  it("fetches and validates the summary levels", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [
        { id: "s-1", level: "brief", word_count: 40, model_used: "llama3", content: "..." },
      ],
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useDocumentSummaries("d-1"), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/compress/documents/d-1/summaries",
      expect.objectContaining({ method: "GET" }),
    );
    expect(result.current.data?.[0].level).toBe("brief");
  });
});
