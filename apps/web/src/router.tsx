import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from "@tanstack/react-router";
import { AppShell } from "@/components/layout/app-shell";
import { PhasePlaceholder } from "@/components/layout/phase-placeholder";
import { OverviewRoute } from "@/features/overview/overview-route";
import { SearchRoute } from "@/features/search/search-route";

const rootRoute = createRootRoute({
  component: () => (
    <AppShell>
      <Outlet />
    </AppShell>
  ),
});

// Inline literal paths so TanStack Router can infer the typed route tree (typed `to`).
const indexRoute = createRoute({ getParentRoute: () => rootRoute, path: "/", component: OverviewRoute });
const searchRoute = createRoute({ getParentRoute: () => rootRoute, path: "/search", component: SearchRoute });

const ingestRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ingest",
  component: () => (
    <PhasePlaceholder
      title="Ingest"
      phase="B"
      summary="Capture documents (POST /documents) and notes (POST /notes) with dedup + provenance."
    />
  ),
});

const compressRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/compress",
  component: () => (
    <PhasePlaceholder
      title="Compress"
      phase="B"
      summary="Summaries, mental models, and embeddings for ingested sources."
    />
  ),
});

const executionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/execution",
  component: () => (
    <PhasePlaceholder
      title="Execution"
      phase="C"
      summary="Roadmaps, goals, and tasks — each with a 'Why' drawer of stored evidence."
    />
  ),
});

const reflectionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/reflection",
  component: () => (
    <PhasePlaceholder
      title="Reflection"
      phase="D"
      summary="Retrospectives and lessons with evidence and supersession lineage."
    />
  ),
});

const observabilityRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/observability",
  component: () => (
    <PhasePlaceholder
      title="Observability"
      phase="E"
      summary="Live health, metrics summary, SLO targets, and docs deep-links."
    />
  ),
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  searchRoute,
  ingestRoute,
  compressRoute,
  executionRoute,
  reflectionRoute,
  observabilityRoute,
]);

export const router = createRouter({ routeTree, defaultPreload: "intent" });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
