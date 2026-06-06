import { cn } from "@/lib/cn";

/** Pulsing placeholder used while content loads. */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-surface-raised", className)} />;
}
