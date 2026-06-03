import { PageHeader } from "./page-header";
import { Card, CardBody } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

/** Keeps the shell fully navigable for screens scheduled in a later build phase. */
export function PhasePlaceholder({
  title,
  phase,
  summary,
}: {
  title: string;
  phase: string;
  summary: string;
}) {
  return (
    <>
      <PageHeader title={title} subtitle={summary} />
      <Card>
        <CardBody className="flex items-center gap-3 text-sm text-zinc-400">
          <Badge tone="info">Phase {phase}</Badge>
          <span>
            This screen is designed and scheduled. It wires the endpoints listed in the
            frontend design doc and reuses the shared provenance components.
          </span>
        </CardBody>
      </Card>
    </>
  );
}
