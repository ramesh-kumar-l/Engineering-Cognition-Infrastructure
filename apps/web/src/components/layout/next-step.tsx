import { Link } from "@tanstack/react-router";
import type { LinkProps } from "@tanstack/react-router";

/** Contextual "next step in the loop" nudge — keeps the workflow self-teaching. */
export function NextStep({ label, to }: { label: string; to: LinkProps["to"] }) {
  return (
    <div className="mt-6 flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-900/40 px-4 py-3 text-sm">
      <span className="text-zinc-400">
        <span className="mr-2 text-zinc-500">Next step →</span>
        {label}
      </span>
      <Link
        to={to}
        className="rounded-md border border-zinc-800 px-3 py-1.5 font-medium text-zinc-200 hover:bg-zinc-800/40"
      >
        Continue
      </Link>
    </div>
  );
}
