import { Link } from "@tanstack/react-router";
import { NAV_ITEMS } from "./nav";
import { cn } from "@/lib/cn";

/** Persistent left rail. Order follows the loop: Ingest → … → Reflection. */
export function Sidebar() {
  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-border bg-surface">
      <div className="flex items-center gap-2.5 px-5 py-4">
        <span className="grid h-7 w-7 place-items-center rounded-md bg-accent-strong text-sm font-bold text-accent-fg">
          E
        </span>
        <div className="leading-tight">
          <div className="text-sm font-semibold tracking-tight text-fg">ECI</div>
          <div className="text-[11px] text-fg-subtle">Engineering Cognition</div>
        </div>
      </div>

      <nav className="flex flex-col gap-0.5 px-3 py-2">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            activeOptions={{ exact: item.path === "/" }}
            className="group rounded-md outline-none"
          >
            {({ isActive }) => (
              <span
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition",
                  isActive
                    ? "bg-surface-raised text-fg"
                    : "text-fg-muted hover:bg-surface-raised hover:text-fg",
                )}
              >
                <span className="w-4 text-center text-fg-subtle group-hover:text-fg-muted">
                  {item.glyph}
                </span>
                <span className="flex-1">{item.label}</span>
                {item.pendingPhase && (
                  <span className="rounded bg-surface-raised px-1.5 py-0.5 text-[10px] text-fg-subtle">
                    P{item.pendingPhase}
                  </span>
                )}
              </span>
            )}
          </Link>
        ))}
      </nav>

      <div className="mt-auto px-5 py-4 text-[11px] text-fg-subtle">
        Evidence-backed · offline-first
      </div>
    </aside>
  );
}
