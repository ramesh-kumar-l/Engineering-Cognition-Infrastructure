import { useAuth } from "@/lib/auth-context";
import { env } from "@/lib/env";
import { HealthPill } from "./health-pill";
import { ThemeToggle } from "./theme-toggle";

/** Top bar: context (actor/auth mode), live health, theme, and a docs deep-link. */
export function Topbar() {
  const { token } = useAuth();

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-surface/70 px-6 backdrop-blur-sm">
      <div className="text-xs text-fg-subtle">
        {token ? "Authenticated session" : "Dev session · auth bypass"}
      </div>
      <div className="flex items-center gap-3">
        <HealthPill />
        <ThemeToggle />
        <a
          href={env.docsUrl}
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-border px-2.5 py-1 text-xs text-fg-muted transition hover:bg-surface-raised hover:text-fg"
        >
          API docs ↗
        </a>
      </div>
    </header>
  );
}
