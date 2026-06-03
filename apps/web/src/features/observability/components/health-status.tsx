import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useHealth, useReadiness } from "../use-health";
import type { Health } from "@/types/api";
import type { UseQueryResult } from "@tanstack/react-query";

interface Probe {
  label: string;
  endpoint: string;
  query: UseQueryResult<Health>;
  okValue: string;
}

function ProbeRow({ label, endpoint, query, okValue }: Probe) {
  const ok = !query.isError && query.data?.status === okValue;
  const tone = query.isLoading ? "neutral" : ok ? "good" : "warn";
  const text = query.isLoading ? "checking" : ok ? query.data!.status : "unreachable";
  return (
    <div className="flex items-center justify-between py-2 text-sm">
      <div className="flex items-center gap-2">
        <span className="font-medium text-zinc-200">{label}</span>
        <code className="font-mono text-xs text-zinc-500">{endpoint}</code>
      </div>
      <Badge tone={tone}>{text}</Badge>
    </div>
  );
}

/** Liveness + readiness probe cards, polled every 15s. */
export function HealthStatus() {
  const health = useHealth();
  const ready = useReadiness();
  const version = health.data?.version;

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <CardTitle>Service health</CardTitle>
        {version && <code className="font-mono text-xs text-zinc-500">eci-api v{version}</code>}
      </CardHeader>
      <CardBody className="divide-y divide-zinc-800/60">
        <ProbeRow label="Liveness" endpoint="/healthz" query={health} okValue="ok" />
        <ProbeRow label="Readiness" endpoint="/readyz" query={ready} okValue="ready" />
      </CardBody>
    </Card>
  );
}
