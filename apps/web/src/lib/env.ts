/** Frontend runtime config. API is reached via the same-origin /api proxy. */
export const env = {
  /** Base path for all API calls; Vite proxies this to the FastAPI backend in dev. */
  apiBase: "/api",
  /** External deep links surfaced in the UI (overridable at build time). */
  docsUrl: "/api/docs",
  redocUrl: "/api/redoc",
  openapiUrl: "/api/openapi.json",
  /** Raw Prometheus exposition endpoint. */
  metricsUrl: "/api/metrics",
  /** Grafana SLO dashboard (prod compose default; not proxied). */
  grafanaUrl: "http://localhost:3000",
} as const;
