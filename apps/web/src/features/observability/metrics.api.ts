import { apiText } from "@/lib/api-client";

/** Compact, UI-friendly rollup of the Prometheus /metrics exposition. */
export interface MetricsSummary {
  totalRequests: number;
  errorRequests: number;
  /** Fraction in [0,1]; SLO-1 style (non-error / total). NaN-safe → 1 when no traffic. */
  successRate: number;
  authDenied: number;
  ingestOps: number;
  /** Mean request latency in milliseconds, or null when no samples yet. */
  avgLatencyMs: number | null;
}

interface Sample {
  name: string;
  labels: Record<string, string>;
  value: number;
}

const SAMPLE = /^([a-zA-Z_:][\w:]*)(\{[^}]*\})?\s+([^\s]+)/;

function parseSample(line: string): Sample | null {
  const m = SAMPLE.exec(line);
  if (!m) return null;
  const labels: Record<string, string> = {};
  if (m[2]) {
    for (const pair of m[2].slice(1, -1).matchAll(/(\w+)="((?:[^"\\]|\\.)*)"/g)) {
      labels[pair[1]] = pair[2];
    }
  }
  const value = Number(m[3]);
  return Number.isNaN(value) ? null : { name: m[1], labels, value };
}

/** Parse raw Prometheus text into the handful of figures the dashboard shows. */
export function parseMetrics(text: string): MetricsSummary {
  let totalRequests = 0;
  let errorRequests = 0;
  let authDenied = 0;
  let ingestOps = 0;
  let latencySum = 0;
  let latencyCount = 0;

  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const s = parseSample(line);
    if (!s) continue;

    switch (s.name) {
      case "eci_requests_total":
        totalRequests += s.value;
        if (s.labels.outcome === "error") errorRequests += s.value;
        break;
      case "eci_auth_denied_total":
        authDenied += s.value;
        break;
      case "eci_ingest_total":
        ingestOps += s.value;
        break;
      case "eci_request_latency_seconds_sum":
        latencySum += s.value;
        break;
      case "eci_request_latency_seconds_count":
        latencyCount += s.value;
        break;
    }
  }

  return {
    totalRequests,
    errorRequests,
    successRate: totalRequests === 0 ? 1 : (totalRequests - errorRequests) / totalRequests,
    authDenied,
    ingestOps,
    avgLatencyMs: latencyCount === 0 ? null : (latencySum / latencyCount) * 1000,
  };
}

export async function getMetrics(signal?: AbortSignal): Promise<MetricsSummary> {
  return parseMetrics(await apiText("/metrics", signal));
}
