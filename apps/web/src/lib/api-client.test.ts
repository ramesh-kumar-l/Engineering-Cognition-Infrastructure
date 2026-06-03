import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  apiRequest,
  ApiError,
  setAuthToken,
  setUnauthorizedHandler,
} from "./api-client";

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText: "STATUS",
    json: async () => body,
  } as Response);
}

describe("apiRequest", () => {
  beforeEach(() => {
    setAuthToken(null);
    setUnauthorizedHandler(null);
  });

  it("parses a JSON response and prefixes the /api base", async () => {
    const fetchMock = mockFetch(200, { status: "ok" });
    vi.stubGlobal("fetch", fetchMock);

    const data = await apiRequest<{ status: string }>("/healthz");

    expect(data).toEqual({ status: "ok" });
    expect(fetchMock).toHaveBeenCalledWith("/api/healthz", expect.objectContaining({ method: "GET" }));
  });

  it("injects the Bearer token when set", async () => {
    const fetchMock = mockFetch(200, {});
    vi.stubGlobal("fetch", fetchMock);
    setAuthToken("tok-123");

    await apiRequest("/goals");

    const headers = fetchMock.mock.calls[0][1].headers as Record<string, string>;
    expect(headers["Authorization"]).toBe("Bearer tok-123");
  });

  it("throws ApiError with the FastAPI detail on non-2xx", async () => {
    vi.stubGlobal("fetch", mockFetch(404, { detail: "not found" }));

    await expect(apiRequest("/goals/x")).rejects.toMatchObject({
      name: "ApiError",
      status: 404,
      detail: "not found",
    });
  });

  it("invokes the unauthorized handler on 401", async () => {
    vi.stubGlobal("fetch", mockFetch(401, { detail: "no token" }));
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);

    await expect(apiRequest("/goals")).rejects.toBeInstanceOf(ApiError);
    expect(onUnauthorized).toHaveBeenCalledOnce();
  });
});
