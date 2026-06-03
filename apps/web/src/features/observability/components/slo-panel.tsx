import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { SLOS, type Slo } from "../slos";

const STATUS_TONE = { live: "good", eval: "info", pending: "neutral" } as const;
const STATUS_LABEL = { live: "measured live", eval: "release gate", pending: "needs prod data" } as const;

function SloRow({ slo }: { slo: Slo }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2 text-sm">
      <div className="min-w-0">
        <span className="font-mono text-xs text-zinc-500">{slo.id}</span>
        <span className="ml-2 font-medium text-zinc-200">{slo.name}</span>
        <span className="ml-2 text-zinc-500">{slo.target}</span>
      </div>
      <Badge tone={STATUS_TONE[slo.status]}>{STATUS_LABEL[slo.status]}</Badge>
    </div>
  );
}

/** Static SLO targets from ADR-010; the success-rate tile above tracks SLO-1 live. */
export function SloPanel() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Service level objectives</CardTitle>
      </CardHeader>
      <CardBody className="divide-y divide-zinc-800/60">
        {SLOS.map((slo) => (
          <SloRow key={slo.id} slo={slo} />
        ))}
      </CardBody>
    </Card>
  );
}
