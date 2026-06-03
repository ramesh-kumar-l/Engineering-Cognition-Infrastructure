import { cn } from "@/lib/cn";

/**
 * Fail-closed trust banner (mirrors AP-2: evidence before inference). When a result
 * carries no resolvable sources, we say so explicitly rather than implying confidence.
 */
export function HasCitationsBanner({
  hasCitations,
  count,
}: {
  hasCitations: boolean;
  count: number;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-2.5 rounded-lg border px-3.5 py-2.5 text-sm",
        hasCitations
          ? "border-emerald-900 bg-emerald-950/40 text-emerald-200"
          : "border-amber-900 bg-amber-950/40 text-amber-200",
      )}
    >
      <span aria-hidden className="text-base leading-none">
        {hasCitations ? "✓" : "⚠"}
      </span>
      {hasCitations ? (
        <span>
          Evidence-backed — {count} source{count === 1 ? "" : "s"} cited. Every claim is
          traceable below.
        </span>
      ) : (
        <span>No sources resolved for this query — treat as unverifiable.</span>
      )}
    </div>
  );
}
