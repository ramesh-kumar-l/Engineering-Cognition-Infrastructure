import { useTheme } from "@/lib/theme";

/** Toggle between dark and light themes. Persists to localStorage. */
export function ThemeToggle() {
  const [theme, setTheme] = useTheme();
  const next = theme === "dark" ? "light" : "dark";
  return (
    <button
      type="button"
      onClick={() => setTheme(next)}
      aria-label={`Switch to ${next} theme`}
      title={`Switch to ${next} theme`}
      className="rounded-md border border-border px-2.5 py-1 text-xs text-fg-muted transition hover:bg-surface-raised hover:text-fg"
    >
      {theme === "dark" ? "☾ Dark" : "☀ Light"}
    </button>
  );
}
