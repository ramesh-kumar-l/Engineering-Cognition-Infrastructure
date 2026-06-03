import { PageHeader } from "@/components/layout/page-header";
import { NextStep } from "@/components/layout/next-step";
import { HealthStatus } from "./components/health-status";
import { MetricsSummary } from "./components/metrics-summary";
import { SloPanel } from "./components/slo-panel";
import { DocsLinks } from "./components/docs-links";

/** Observability screen: live health, metrics rollup, SLO targets, and docs deep-links. */
export function ObservabilityRoute() {
  return (
    <>
      <PageHeader
        title="Observability"
        subtitle="Live health, request metrics, and the SLOs the system is held to."
      />

      <MetricsSummary />

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <HealthStatus />
        <SloPanel />
      </div>

      <div className="mt-4">
        <DocsLinks />
      </div>

      <NextStep label="Capture new sources to keep the loop turning." to="/ingest" />
    </>
  );
}
