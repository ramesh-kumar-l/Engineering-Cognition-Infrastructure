import { Link } from "@tanstack/react-router";
import { NAV_ITEMS } from "./nav";
import { cn } from "@/lib/cn";

/** Persistent left rail. Order follows the loop: Ingest → … → Reflection. */
export function Sidebar() {
  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-zinc-800 bg-zinc-950/80">
      <div className="flex items-center gap-2.5 px-5 py-4">
        <span className="grid h-7 w-7 place-items-center rounded-md bg-[--color-accent-strong] text-sm font-bold text-zinc-50">
          E
        </span>
        <div className="leading-tight">
          <div className="text-sm font-semibold tracking-tight">ECI</div>
          <div className="text-[11px] text-zinc-500">Engineering Cognition</div>
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
                    ? "bg-zinc-800/70 text-zinc-100"
                    : "text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-200",
                )}
              >
                <span className="w-4 text-center text-zinc-500 group-hover:text-zinc-300">
                  {item.glyph}
                </span>
                <span className="flex-1">{item.label}</span>
                {item.pendingPhase && (
                  <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-500">
                    P{item.pendingPhase}
                  </span>
                )}
              </span>
            )}
          </Link>
        ))}
      </nav>

      <div className="mt-auto px-5 py-4 text-[11px] text-zinc-600">
        Evidence-backed · offline-first
      </div>
    </aside>
  );
}
