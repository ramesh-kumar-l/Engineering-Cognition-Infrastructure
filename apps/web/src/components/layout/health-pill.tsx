import { useHealth } from "@/features/observability/use-health";
import { cn } from "@/lib/cn";

/** Live backend status indicator. Green when /healthz returns ok. */
export function HealthPill() {
  const { data, isLoading, isError } = useHealth();
  const ok = !isError && data?.status === "ok";

  const tone = isLoading
    ? { dot: "bg-zinc-500", text: "text-zinc-400", label: "checking" }
    : ok
      ? { dot: "bg-emerald-400", text: "text-emerald-300", label: "API healthy" }
      : { dot: "bg-red-400", text: "text-red-300", label: "API unreachable" };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/60 px-2.5 py-1 text-xs",
        tone.text,
      )}
      title={data?.version ? `eci-api v${data.version}` : undefined}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", tone.dot, !isLoading && ok && "animate-pulse")} />
      {tone.label}
    </span>
  );
}
