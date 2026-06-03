import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from "@tanstack/react-router";
import { AppShell } from "@/components/layout/app-shell";
import { OverviewRoute } from "@/features/overview/overview-route";
import { SearchRoute } from "@/features/search/search-route";
import { IngestRoute } from "@/features/ingest/ingest-route";
import { CompressRoute } from "@/features/compress/compress-route";
import { ExecutionRoute } from "@/features/execution/execution-route";
import { ReflectionRoute } from "@/features/reflection/reflection-route";
import { ObservabilityRoute } from "@/features/observability/observability-route";

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
  component: IngestRoute,
});

const compressRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/compress",
  component: CompressRoute,
  validateSearch: (search: Record<string, unknown>): { documentId?: string } => ({
    documentId: typeof search.documentId === "string" ? search.documentId : undefined,
  }),
});

const executionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/execution",
  component: ExecutionRoute,
});

const reflectionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/reflection",
  component: ReflectionRoute,
});

const observabilityRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/observability",
  component: ObservabilityRoute,
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
