import { env } from "./env";

/** Raised for any non-2xx response; `detail` mirrors FastAPI's error body. */
export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

let authToken: string | null = null;
let unauthorizedHandler: (() => void) | null = null;

/** Set/clear the Bearer token injected into every request (OIDC-ready). */
export function setAuthToken(token: string | null): void {
  authToken = token;
}

/** Current Bearer token, for callers that issue their own fetch (e.g. streaming). */
export function getAuthToken(): string | null {
  return authToken;
}

/** Invoke the registered 401 handler (used by non-apiRequest fetch paths). */
export function notifyUnauthorized(): void {
  unauthorizedHandler?.();
}

/** Register a callback invoked whenever the API returns 401. */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

interface RequestOptions<T> {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  /** JSON body (object) or FormData for multipart uploads. */
  body?: unknown;
  /** Optional parser (e.g. a Zod schema) to validate and type the response. */
  schema?: { parse: (data: unknown) => T };
  signal?: AbortSignal;
}

async function parseDetail(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (data && typeof data.detail === "string") return data.detail;
    return res.statusText;
  } catch {
    return res.statusText;
  }
}

/** Typed fetch wrapper: injects auth, handles 401, parses + validates the response. */
export async function apiRequest<T = unknown>(
  path: string,
  options: RequestOptions<T> = {},
): Promise<T> {
  const { method = "GET", body, schema, signal } = options;
  const isForm = body instanceof FormData;

  const headers: Record<string, string> = {};
  if (body !== undefined && !isForm) headers["Content-Type"] = "application/json";
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

  const res = await fetch(`${env.apiBase}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : isForm ? (body as FormData) : JSON.stringify(body),
    signal,
  });

  if (res.status === 401) {
    unauthorizedHandler?.();
    throw new ApiError(401, await parseDetail(res));
  }
  if (!res.ok) {
    throw new ApiError(res.status, await parseDetail(res));
  }

  if (res.status === 204) return undefined as T;

  const data = await res.json();
  return schema ? schema.parse(data) : (data as T);
}

/** Like apiRequest, but returns the raw response body as text (e.g. Prometheus /metrics). */
export async function apiText(path: string, signal?: AbortSignal): Promise<string> {
  const headers: Record<string, string> = {};
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

  const res = await fetch(`${env.apiBase}${path}`, { headers, signal });
  if (res.status === 401) {
    unauthorizedHandler?.();
    throw new ApiError(401, await parseDetail(res));
  }
  if (!res.ok) throw new ApiError(res.status, await parseDetail(res));
  return res.text();
}
