import { useState, type ReactNode } from "react";
import { cn } from "@/lib/cn";

export interface TabItem {
  id: string;
  label: string;
  /** Optional trailing count badge. */
  count?: number;
  content: ReactNode;
}

/** Minimal, accessible tabs — local (no extra dependency). */
export function Tabs({ items, initial }: { items: TabItem[]; initial?: string }) {
  const [active, setActive] = useState(initial ?? items[0]?.id);
  const current = items.find((i) => i.id === active) ?? items[0];

  return (
    <div>
      <div role="tablist" className="flex gap-1 border-b border-border">
        {items.map((item) => {
          const selected = item.id === current?.id;
          return (
            <button
              key={item.id}
              role="tab"
              type="button"
              aria-selected={selected}
              onClick={() => setActive(item.id)}
              className={cn(
                "-mb-px border-b-2 px-3.5 py-2 text-sm font-medium transition outline-none",
                selected
                  ? "border-accent text-fg"
                  : "border-transparent text-fg-muted hover:text-fg",
              )}
            >
              {item.label}
              {item.count !== undefined && (
                <span className="ml-1.5 text-xs text-fg-subtle">{item.count}</span>
              )}
            </button>
          );
        })}
      </div>
      <div role="tabpanel" className="pt-4">
        {current?.content}
      </div>
    </div>
  );
}
