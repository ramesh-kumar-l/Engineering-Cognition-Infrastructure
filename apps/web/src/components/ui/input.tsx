import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full rounded-md border border-zinc-700 bg-zinc-900/60 px-3.5 py-2 text-sm text-zinc-100",
        "placeholder:text-zinc-500 outline-none transition",
        "focus-visible:border-[--color-accent] focus-visible:ring-2 focus-visible:ring-[--color-accent]/40",
        className,
      )}
      {...props}
    />
  );
}
