import { describe, it, expect } from "vitest";
import { parseMetrics } from "./metrics.api";

const SAMPLE = `
# HELP eci_requests_total Total inbound requests handled.
# TYPE eci_requests_total counter
eci_requests_total{route="/healthz",method="GET",outcome="ok"} 40.0
eci_requests_total{route="/retrieval/search",method="POST",outcome="ok"} 8.0
eci_requests_total{route="/retrieval/search",method="POST",outcome="error"} 2.0
# TYPE eci_auth_denied_total counter
eci_auth_denied_total{reason="missing_token"} 3.0
# TYPE eci_ingest_total counter
eci_ingest_total{source_kind="document",outcome="create"} 5.0
# TYPE eci_request_latency_seconds histogram
eci_request_latency_seconds_sum{route="/retrieval/search",method="POST"} 5.0
eci_request_latency_seconds_count{route="/retrieval/search",method="POST"} 10.0
`;

describe("parseMetrics", () => {
  it("rolls up counters and computes success rate + avg latency", () => {
    const m = parseMetrics(SAMPLE);
    expect(m.totalRequests).toBe(50);
    expect(m.errorRequests).toBe(2);
    expect(m.successRate).toBeCloseTo(0.96, 5);
    expect(m.authDenied).toBe(3);
    expect(m.ingestOps).toBe(5);
    expect(m.avgLatencyMs).toBe(500);
  });

  it("is NaN-safe with no traffic", () => {
    const m = parseMetrics("# empty\n");
    expect(m.totalRequests).toBe(0);
    expect(m.successRate).toBe(1);
    expect(m.avgLatencyMs).toBeNull();
  });
});
