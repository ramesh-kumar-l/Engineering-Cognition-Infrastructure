import { useCallback, useRef, useState } from "react";
import { ApiError } from "@/lib/api-client";
import { AssistantCitationsSchema, type Citation } from "@/types/api";
import { streamAssistant } from "./assistant.api";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  /** Cited sources (assistant turns). */
  citations?: Citation[];
  /** Whether the backend resolved evidence; false → fail-closed (AP-2). */
  hasCitations?: boolean;
  /** Still receiving tokens. */
  streaming?: boolean;
  /** Set when the request failed. */
  error?: string;
}

/** Conversation state + streaming for the grounded assistant. */
export function useAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const idRef = useRef(0);

  const patch = useCallback((id: string, updater: (m: ChatMessage) => ChatMessage) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? updater(m) : m)));
  }, []);

  const send = useCallback(
    async (query: string) => {
      const userId = `u${idRef.current++}`;
      const botId = `a${idRef.current++}`;
      setMessages((prev) => [
        ...prev,
        { id: userId, role: "user", content: query },
        { id: botId, role: "assistant", content: "", streaming: true },
      ]);
      setIsStreaming(true);
      const ac = new AbortController();
      abortRef.current = ac;

      try {
        await streamAssistant(
          query,
          {
            onToken: (text) => patch(botId, (m) => ({ ...m, content: m.content + text })),
            onEvent: (event, data) => {
              if (event !== "citations") return;
              const parsed = AssistantCitationsSchema.safeParse(data);
              if (parsed.success) {
                patch(botId, (m) => ({
                  ...m,
                  hasCitations: parsed.data.has_citations,
                  citations: parsed.data.citations,
                }));
              }
            },
          },
          ac.signal,
        );
      } catch (e) {
        if (!ac.signal.aborted) {
          const detail = e instanceof ApiError ? e.detail : "Assistant request failed";
          patch(botId, (m) => ({ ...m, error: detail }));
        }
      } finally {
        patch(botId, (m) => ({ ...m, streaming: false }));
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [patch],
  );

  const stop = useCallback(() => abortRef.current?.abort(), []);

  return { messages, isStreaming, send, stop };
}
