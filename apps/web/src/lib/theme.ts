import { useEffect, useState } from "react";

export type Theme = "dark" | "light";

const STORAGE_KEY = "eci-theme";

/** Read the persisted theme, falling back to dark (the product default). */
export function getInitialTheme(): Theme {
  if (typeof localStorage !== "undefined") {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
  }
  return "dark";
}

/** Apply a theme to <html> and persist it. */
export function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  if (typeof localStorage !== "undefined") localStorage.setItem(STORAGE_KEY, theme);
}

/** Theme state hook: applies on mount and on every change. */
export function useTheme(): [Theme, (t: Theme) => void] {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  useEffect(() => {
    applyTheme(theme);
  }, [theme]);
  return [theme, setTheme];
}
