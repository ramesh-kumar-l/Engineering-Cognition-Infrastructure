import { describe, it, expect, vi } from "vitest";
import type { ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useCreateRoadmap, useGoalWhy, useUpdateGoalStatus } from "./use-execution";

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

describe("useCreateRoadmap", () => {
  it("posts the roadmap and returns the validated result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({ id: "r-1", title: "Q3 Platform", description: null }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useCreateRoadmap(), { wrapper: wrapper() });
    result.current.mutate({ title: "Q3 Platform" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith("/api/roadmaps", expect.objectContaining({ method: "POST" }));
    expect(result.current.data?.id).toBe("r-1");
  });
});

describe("useUpdateGoalStatus", () => {
  it("PATCHes the goal status endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: "g-1",
        title: "Ship retrieval",
        description: null,
        status: "in_progress",
        roadmap_id: "r-1",
        source_memory_id: null,
      }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useUpdateGoalStatus(), { wrapper: wrapper() });
    result.current.mutate({ id: "g-1", input: { status: "in_progress" } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/goals/g-1/status",
      expect.objectContaining({ method: "PATCH" }),
    );
    expect(result.current.data?.status).toBe("in_progress");
  });
});

describe("useGoalWhy", () => {
  it("fetches stored citations for a goal when enabled", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [
        {
          target_type: "goal",
          target_id: "g-1",
          source_type: "document",
          source_id: "d-1",
          chunk_index: 0,
          content: "evidence",
          score: 0.91,
          title: "ADR-006",
          source_uri: "repo://adr-006",
        },
      ],
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useGoalWhy("g-1", true), { wrapper: wrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/goals/g-1/why",
      expect.objectContaining({ method: "GET" }),
    );
    expect(result.current.data?.[0].source_id).toBe("d-1");
  });
});
