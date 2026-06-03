import type { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type Variant = "primary" | "ghost" | "outline";

const variants: Record<Variant, string> = {
  primary:
    "bg-[--color-accent-strong] text-zinc-50 hover:brightness-110 focus-visible:ring-[--color-accent]",
  ghost: "text-zinc-300 hover:bg-zinc-800/60 focus-visible:ring-zinc-600",
  outline:
    "border border-zinc-700 text-zinc-200 hover:bg-zinc-800/40 focus-visible:ring-zinc-600",
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

export function Button({ variant = "primary", className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md px-3.5 py-2 text-sm font-medium",
        "transition outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
