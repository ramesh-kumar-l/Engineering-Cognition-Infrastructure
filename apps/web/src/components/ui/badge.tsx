import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type Tone = "neutral" | "good" | "warn" | "info";

const tones: Record<Tone, string> = {
  neutral: "border-border bg-surface-raised text-fg-muted",
  good: "border-success/40 bg-success-soft text-success",
  warn: "border-warning/40 bg-warning-soft text-warning",
  info: "border-accent/40 bg-accent/10 text-accent",
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

export function Badge({ tone = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
      {...props}
    />
  );
}
