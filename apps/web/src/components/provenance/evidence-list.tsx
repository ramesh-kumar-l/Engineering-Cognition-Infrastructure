import type { Evidence } from "@/types/api";
import { Badge } from "@/components/ui/badge";

/**
 * Renders the evidence behind a lesson. Fail-closed (AP-2): a lesson with no
 * evidence is shown as explicitly unverifiable rather than silently trusted.
 */
export function EvidenceList({ evidence }: { evidence: Evidence[] }) {
  if (evidence.length === 0) {
    return (
      <p className="rounded-md border border-amber-800 bg-amber-950/30 px-3 py-2 text-xs text-amber-300">
        No evidence — this lesson is unverifiable.
      </p>
    );
  }

  return (
    <ul className="space-y-1.5">
      {evidence.map((e) => (
        <li
          key={e.id}
          className="rounded-md border border-zinc-800 bg-zinc-900/40 px-3 py-2"
        >
          <div className="flex items-center gap-2">
            <Badge tone="info">{e.source_type}</Badge>
            <span className="font-mono text-[11px] text-zinc-500">
              id {e.source_id.slice(0, 8)}
            </span>
          </div>
          {e.summary && <p className="mt-1 text-xs text-zinc-300">{e.summary}</p>}
        </li>
      ))}
    </ul>
  );
}
