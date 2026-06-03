import { Badge } from "@/components/ui/badge";

/** Shows how many candidates each retrieval stage (bm25 / semantic) contributed. */
export function RetrievalStagesChip({ stages }: { stages: Record<string, number> }) {
  const entries = Object.entries(stages);
  if (entries.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-xs text-zinc-500">Retrieval:</span>
      {entries.map(([stage, n]) => (
        <Badge key={stage} tone="info">
          {stage} · {n}
        </Badge>
      ))}
    </div>
  );
}
