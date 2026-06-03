import { useAuth } from "@/lib/auth-context";
import { env } from "@/lib/env";
import { HealthPill } from "./health-pill";

/** Top bar: context (actor/auth mode), live health, and a docs deep-link. */
export function Topbar() {
  const { token } = useAuth();

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-zinc-800 bg-zinc-950/60 px-6">
      <div className="text-xs text-zinc-500">
        {token ? "Authenticated session" : "Dev session · auth bypass"}
      </div>
      <div className="flex items-center gap-3">
        <HealthPill />
        <a
          href={env.docsUrl}
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-zinc-800 px-2.5 py-1 text-xs text-zinc-400 transition hover:bg-zinc-800/40 hover:text-zinc-200"
        >
          API docs ↗
        </a>
      </div>
    </header>
  );
}
