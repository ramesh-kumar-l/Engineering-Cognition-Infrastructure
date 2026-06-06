import { Link } from "@tanstack/react-router";
import type { Citation } from "@/types/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function formatScore(score: Citation["score"]): string | null {
  if (score === null || score === undefined) return null;
  return score.toFixed(3);
}

/** Renders one piece of evidence with its full provenance: title, source, score, chunk. */
export function CitationCard({ citation, rank }: { citation: Citation; rank: number }) {
  const score = formatScore(citation.score);

  return (
    <Card className="overflow-hidden">
      <div className="flex items-start justify-between gap-3 border-b border-border px-4 py-2.5">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="font-mono text-xs text-fg-subtle">#{rank}</span>
          <span className="truncate text-sm font-medium text-fg">
            {citation.title ?? "Untitled source"}
          </span>
        </div>
        <div className="flex shrink-0 items-center gap-1.5">
          <Badge tone="neutral">{citation.source_type}</Badge>
          {score && <Badge tone="good">score {score}</Badge>}
        </div>
      </div>

      <div className="px-4 py-3">
        <p className="line-clamp-4 text-sm leading-relaxed text-fg-muted">{citation.content}</p>
      </div>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-border px-4 py-2 text-[11px] text-fg-subtle">
        {citation.source_uri && (
          <span className="truncate font-mono">{citation.source_uri}</span>
        )}
        <span className="font-mono">id {citation.source_id.slice(0, 8)}</span>
        {citation.chunk_index !== null && citation.chunk_index !== undefined && (
          <span className="font-mono">chunk {citation.chunk_index}</span>
        )}
        {citation.source_type === "document" && (
          <Link
            to="/documents/$id"
            params={{ id: citation.source_id }}
            className="ml-auto text-accent hover:brightness-110"
          >
            View document ↗
          </Link>
        )}
      </div>
    </Card>
  );
}
