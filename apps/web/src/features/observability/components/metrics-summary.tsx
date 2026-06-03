import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { useMetrics } from "../use-metrics";
import type { MetricsSummary as Summary } from "../metrics.api";

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 px-4 py-3">
      <div className="text-xs uppercase tracking-wide text-zinc-500">{label}</div>
      <div className="mt-1 font-mono text-lg text-zinc-100">{value}</div>
      {hint && <div className="mt-0.5 text-xs text-zinc-500">{hint}</div>}
    </div>
  );
}

function tiles(m: Summary) {
  return [
    { label: "Requests", value: m.totalRequests.toLocaleString(), hint: `${m.errorRequests} errors` },
    { label: "Success rate", value: `${(m.successRate * 100).toFixed(2)}%`, hint: "SLO-1 ≥ 99.5%" },
    { label: "Avg latency", value: m.avgLatencyMs === null ? "—" : `${m.avgLatencyMs.toFixed(0)} ms`, hint: "all routes" },
    { label: "Auth denials", value: m.authDenied.toLocaleString(), hint: "RBAC + token" },
    { label: "Ingest ops", value: m.ingestOps.toLocaleString(), hint: "documents + notes" },
  ];
}

/** Live counters rolled up from Prometheus /metrics. Fails closed when unreachable. */
export function MetricsSummary() {
  const { data, isLoading, isError } = useMetrics();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Live metrics</CardTitle>
      </CardHeader>
      <CardBody>
        {isLoading && <p className="text-sm text-zinc-500">Reading /metrics…</p>}
        {isError && (
          <p className="text-sm text-amber-300">
            /metrics is unreachable — counters unavailable.
          </p>
        )}
        {data && (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
            {tiles(data).map((t) => (
              <Stat key={t.label} {...t} />
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
