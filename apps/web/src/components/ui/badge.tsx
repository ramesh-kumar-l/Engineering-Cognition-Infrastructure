import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type Tone = "neutral" | "good" | "warn" | "info";

const tones: Record<Tone, string> = {
  neutral: "border-zinc-700 bg-zinc-800/50 text-zinc-300",
  good: "border-emerald-800 bg-emerald-950/50 text-emerald-300",
  warn: "border-amber-800 bg-amber-950/50 text-amber-300",
  info: "border-sky-800 bg-sky-950/50 text-sky-300",
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
