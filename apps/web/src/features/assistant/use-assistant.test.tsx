import { describe, it, expect, vi, beforeEach } from "vitest";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { StreamHandlers } from "@/lib/stream";
import { useAssistant } from "./use-assistant";
import { streamAssistant } from "./assistant.api";

vi.mock("./assistant.api", () => ({ streamAssistant: vi.fn() }));
const mockStream = vi.mocked(streamAssistant);

const CITATION = {
  source_type: "document",
  source_id: "11111111-2222-3333-4444-555555555555",
  chunk_index: 1,
  content: "evidence",
  score: 0.9,
  title: "Doc",
  source_uri: null,
};

describe("useAssistant", () => {
  beforeEach(() => mockStream.mockReset());

  it("accumulates streamed tokens and attaches citations", async () => {
    mockStream.mockImplementation(async (_q, handlers: StreamHandlers) => {
      handlers.onToken?.("Hello ");
      handlers.onToken?.("world [1]");
      handlers.onEvent?.("citations", { has_citations: true, citations: [CITATION] });
    });

    const { result } = renderHook(() => useAssistant());
    await act(async () => {
      await result.current.send("why?");
    });

    const bot = result.current.messages.find((m) => m.role === "assistant")!;
    expect(bot.content).toBe("Hello world [1]");
    expect(bot.hasCitations).toBe(true);
    expect(bot.citations).toHaveLength(1);
    expect(bot.streaming).toBe(false);
  });

  it("fails closed: no tokens, has_citations false, empty answer", async () => {
    mockStream.mockImplementation(async (_q, handlers: StreamHandlers) => {
      handlers.onEvent?.("citations", { has_citations: false, citations: [] });
    });

    const { result } = renderHook(() => useAssistant());
    await act(async () => {
      await result.current.send("obscure");
    });

    const bot = result.current.messages.find((m) => m.role === "assistant")!;
    expect(bot.content).toBe("");
    expect(bot.hasCitations).toBe(false);
    expect(bot.citations).toEqual([]);
  });

  it("records an error when the stream throws", async () => {
    mockStream.mockImplementation(async () => {
      throw new Error("boom");
    });

    const { result } = renderHook(() => useAssistant());
    await act(async () => {
      await result.current.send("q");
    });

    await waitFor(() => {
      const bot = result.current.messages.find((m) => m.role === "assistant")!;
      expect(bot.error).toBeTruthy();
    });
  });
});
