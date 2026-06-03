import type { Summary } from "@/types/api";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

/** Renders the document's summary levels (brief → standard → detailed). */
export function SummaryList({ summaries }: { summaries: Summary[] }) {
  if (summaries.length === 0) {
    return (
      <Card>
        <CardBody className="text-sm text-zinc-400">
          No summaries yet. Run compression to generate them.
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {summaries.map((s) => (
        <Card key={s.id}>
          <CardHeader className="flex items-center justify-between gap-3">
            <CardTitle className="capitalize">{s.level}</CardTitle>
            <div className="flex items-center gap-2">
              <Badge tone="info">{s.word_count} words</Badge>
              <Badge tone="neutral" className="font-mono">
                {s.model_used}
              </Badge>
            </div>
          </CardHeader>
          <CardBody className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-300">
            {s.content}
          </CardBody>
        </Card>
      ))}
    </div>
  );
}
