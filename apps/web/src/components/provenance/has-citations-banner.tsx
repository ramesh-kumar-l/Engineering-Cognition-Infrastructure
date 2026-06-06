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
          ? "border-success/40 bg-success-soft text-success"
          : "border-warning/40 bg-warning-soft text-warning",
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
