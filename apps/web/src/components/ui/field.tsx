import type { ReactNode } from "react";

/** Labeled form control wrapper for consistent spacing + typography. */
export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="block space-y-1.5">
      <span className="text-xs font-medium text-fg-muted">{label}</span>
      {children}
      {hint && <span className="block text-xs text-fg-subtle">{hint}</span>}
    </label>
  );
}
