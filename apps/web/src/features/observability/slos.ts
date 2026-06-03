/** Service Level Objectives, mirrored from project-memory-bank/slos/slos.md (ADR-010). */
export interface Slo {
  id: string;
  name: string;
  target: string;
  /** "live" = computable from /metrics now; "eval" = per-release gate; "pending" = needs prod traffic. */
  status: "live" | "eval" | "pending";
}

export const SLOS: Slo[] = [
  { id: "SLO-1", name: "Availability", target: "≥ 99.5% success / 7d", status: "live" },
  { id: "SLO-2", name: "Latency p95", target: "≤ 500ms", status: "pending" },
  { id: "SLO-3", name: "Latency p99", target: "≤ 1500ms", status: "pending" },
  { id: "SLO-4", name: "Citation coverage", target: "100% of retrievals cited", status: "eval" },
  { id: "SLO-5", name: "Retrieval Recall@5", target: "≥ 0.70", status: "eval" },
];
