/** Navigation mirrors the cognition loop so the tool teaches its own workflow. */
export interface NavItem {
  path: string;
  label: string;
  /** Loop-stage glyph (kept ASCII-simple for a calm, technical surface). */
  glyph: string;
  /** Phase that lights this screen up; null = live now. */
  pendingPhase: string | null;
}

export const NAV_ITEMS: NavItem[] = [
  { path: "/", label: "Overview", glyph: "◎", pendingPhase: null },
  { path: "/ingest", label: "Ingest", glyph: "↧", pendingPhase: null },
  { path: "/compress", label: "Compress", glyph: "⊟", pendingPhase: null },
  { path: "/search", label: "Search", glyph: "⌕", pendingPhase: null },
  { path: "/execution", label: "Execution", glyph: "▤", pendingPhase: null },
  { path: "/reflection", label: "Reflection", glyph: "↻", pendingPhase: null },
  { path: "/observability", label: "Observability", glyph: "❤", pendingPhase: null },
];
