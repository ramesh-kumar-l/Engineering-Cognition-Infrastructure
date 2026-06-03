import { describe, it, expect, vi } from "vitest";
import type { ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useIngestDocument, useIngestNote } from "./use-ingest";

function wrapper() {
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

describe("useIngestNote", () => {
  it("posts the note as JSON and returns the validated result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: "n-1",
        content_hash: "abc123",
        source: "meeting://standup",
        deduplicated: false,
        ingested_at: "2026-06-03T10:00:00Z",
      }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useIngestNote(), { wrapper: wrapper() });
    result.current.mutate({ body: "decision", source: "meeting://standup" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith("/api/notes", expect.objectContaining({ method: "POST" }));
    expect(result.current.data?.id).toBe("n-1");
    expect(result.current.data?.deduplicated).toBe(false);
  });
});

describe("useIngestDocument", () => {
  it("posts multipart FormData to /documents", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: "d-1",
        content_hash: "hash",
        kind: "markdown",
        title: "ADR-006",
        source: "repo://adr-006",
        deduplicated: true,
        ingested_at: "2026-06-03T10:00:00Z",
      }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const file = new File(["# hi"], "adr.md", { type: "text/markdown" });
    const { result } = renderHook(() => useIngestDocument(), { wrapper: wrapper() });
    result.current.mutate({ file, kind: "markdown", source: "repo://adr-006" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/documents");
    expect(init.body).toBeInstanceOf(FormData);
    expect(result.current.data?.deduplicated).toBe(true);
  });
});
