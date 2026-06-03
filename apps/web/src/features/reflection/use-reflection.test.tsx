import { describe, it, expect, vi } from "vitest";
import type { ReactNode } from "react";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useCreateLesson, useCreateRetrospective, useSupersedeLesson } from "./use-reflection";

function wrapper() {
  const client = new QueryClient({
    defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

describe("useCreateRetrospective", () => {
  it("posts the retrospective and returns the validated result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: "retro-1",
        cadence: "weekly",
        scope_type: null,
        scope_id: null,
        status: "completed",
        lesson_count: 0,
        notes: null,
      }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useCreateRetrospective(), { wrapper: wrapper() });
    result.current.mutate({ cadence: "weekly" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/retrospectives",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.current.data?.id).toBe("retro-1");
  });
});

describe("useCreateLesson", () => {
  it("posts a lesson with its evidence and returns the validated result", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: "lesson-1",
        retrospective_id: null,
        claim: "RRF beats neural rerank here",
        scope: "global",
        confidence: "high",
        status: "active",
        supersedes_id: null,
        evidence: [{ id: "ev-1", source_type: "goal", source_id: "g-1", summary: "shipped" }],
      }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useCreateLesson(), { wrapper: wrapper() });
    result.current.mutate({ claim: "RRF beats neural rerank here", confidence: "high" });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/lessons",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.current.data?.evidence[0].source_id).toBe("g-1");
  });
});

describe("useSupersedeLesson", () => {
  it("posts to the supersede endpoint for the given lesson", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: "lesson-2",
        retrospective_id: null,
        claim: "Revised belief",
        scope: "global",
        confidence: "medium",
        status: "active",
        supersedes_id: "lesson-1",
        evidence: [],
      }),
    } as Response);
    vi.stubGlobal("fetch", fetchMock);

    const { result } = renderHook(() => useSupersedeLesson(), { wrapper: wrapper() });
    result.current.mutate({ id: "lesson-1", input: { claim: "Revised belief" } });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/lessons/lesson-1/supersede",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.current.data?.supersedes_id).toBe("lesson-1");
  });
});
