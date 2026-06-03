import { Link } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { env } from "@/lib/env";

interface Stage {
  step: number;
  title: string;
  blurb: string;
  to: string;
  live: boolean;
}

const STAGES: Stage[] = [
  { step: 1, title: "Ingest", blurb: "Capture documents and notes with full provenance.", to: "/ingest", live: false },
  { step: 2, title: "Compress", blurb: "Summaries, mental models, and embeddings.", to: "/compress", live: false },
  { step: 3, title: "Search", blurb: "Hybrid retrieval — answers with their sources.", to: "/search", live: true },
  { step: 4, title: "Execution", blurb: "Goals and tasks linked to the evidence behind them.", to: "/execution", live: false },
  { step: 5, title: "Reflection", blurb: "Retrospectives distil lessons from outcomes.", to: "/reflection", live: false },
];

export function OverviewRoute() {
  return (
    <>
      <PageHeader
        title="Welcome to ECI"
        subtitle="Trustworthy engineering memory. Follow the loop — every step keeps its evidence."
      />

      <Card className="mb-6">
        <CardBody className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm text-zinc-300">
            <span className="font-medium text-zinc-100">Start here:</span> run a search to see
            provenance in action, then ingest your own sources.
          </div>
          <div className="flex gap-2 text-sm">
            <Link to="/search" className="rounded-md bg-[--color-accent-strong] px-3 py-1.5 font-medium text-zinc-50 hover:brightness-110">
              Try Search →
            </Link>
            <a href={env.docsUrl} target="_blank" rel="noreferrer" className="rounded-md border border-zinc-800 px-3 py-1.5 text-zinc-300 hover:bg-zinc-800/40">
              API docs ↗
            </a>
          </div>
        </CardBody>
      </Card>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {STAGES.map((s) => (
          <Link key={s.title} to={s.to} className="outline-none">
            <Card className="h-full transition hover:border-zinc-700">
              <CardHeader className="flex items-center justify-between">
                <CardTitle>
                  <span className="mr-2 font-mono text-zinc-600">{s.step}</span>
                  {s.title}
                </CardTitle>
                <Badge tone={s.live ? "good" : "neutral"}>{s.live ? "live" : "soon"}</Badge>
              </CardHeader>
              <CardBody className="text-sm text-zinc-400">{s.blurb}</CardBody>
            </Card>
          </Link>
        ))}
      </div>
    </>
  );
}
