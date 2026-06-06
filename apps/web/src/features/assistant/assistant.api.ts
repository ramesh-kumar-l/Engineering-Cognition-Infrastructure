import { streamSse, type StreamHandlers } from "@/lib/stream";

/** Stream a grounded answer from POST /assistant/stream (SSE). */
export function streamAssistant(
  query: string,
  handlers: StreamHandlers,
  signal?: AbortSignal,
  topK = 8,
): Promise<void> {
  return streamSse("/assistant/stream", { query, top_k: topK }, handlers, signal);
}
