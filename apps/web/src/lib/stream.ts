import { ApiError, getAuthToken, notifyUnauthorized } from "./api-client";
import { env } from "./env";

/** Callbacks for a server-sent-event stream. */
export interface StreamHandlers {
  /** A `token` frame: an incremental chunk of answer text. */
  onToken?: (text: string) => void;
  /** A named frame other than `token` (e.g. `citations`), with parsed JSON data. */
  onEvent?: (event: string, data: unknown) => void;
}

interface SseFrame {
  event: string;
  data: string;
}

function parseFrame(raw: string): SseFrame | null {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (dataLines.length === 0) return null;
  return { event, data: dataLines.join("\n") };
}

/**
 * POST `body` as JSON to `path` and consume a `text/event-stream` response,
 * dispatching frames to `handlers`. Injects the Bearer token and honors `signal`.
 */
export async function streamSse(
  path: string,
  body: unknown,
  handlers: StreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getAuthToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${env.apiBase}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    signal,
  });

  if (res.status === 401) {
    notifyUnauthorized();
    throw new ApiError(401, "Authorization required");
  }
  if (!res.ok || !res.body) {
    throw new ApiError(res.status, res.statusText || "Stream failed");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const frame = parseFrame(buffer.slice(0, sep));
      buffer = buffer.slice(sep + 2);
      if (!frame) continue;
      if (frame.event === "token") {
        const parsed = JSON.parse(frame.data) as { text?: string };
        if (parsed.text) handlers.onToken?.(parsed.text);
      } else {
        handlers.onEvent?.(frame.event, safeJson(frame.data));
      }
    }
  }
}

function safeJson(raw: string): unknown {
  try {
    return JSON.parse(raw);
  } catch {
    return raw;
  }
}
