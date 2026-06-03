import type { SelectHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cn(
        "rounded-md border border-zinc-700 bg-zinc-900/60 px-3 py-2 text-sm text-zinc-100",
        "outline-none transition focus-visible:border-[--color-accent] focus-visible:ring-2 focus-visible:ring-[--color-accent]/40",
        className,
      )}
      {...props}
    />
  );
}
