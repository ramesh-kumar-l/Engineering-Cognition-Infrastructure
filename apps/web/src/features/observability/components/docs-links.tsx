import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { env } from "@/lib/env";

interface DeepLink {
  label: string;
  href: string;
  blurb: string;
}

const LINKS: DeepLink[] = [
  { label: "Swagger UI", href: env.docsUrl, blurb: "Interactive OpenAPI explorer" },
  { label: "ReDoc", href: env.redocUrl, blurb: "Reference API documentation" },
  { label: "OpenAPI schema", href: env.openapiUrl, blurb: "Raw openapi.json" },
  { label: "Grafana", href: env.grafanaUrl, blurb: "SLO dashboard (prod stack)" },
  { label: "Raw /metrics", href: env.metricsUrl, blurb: "Prometheus exposition" },
];

/** Deep links to the system's docs and observability surfaces. */
export function DocsLinks() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Docs &amp; dashboards</CardTitle>
      </CardHeader>
      <CardBody className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {LINKS.map((l) => (
          <a
            key={l.label}
            href={l.href}
            target="_blank"
            rel="noreferrer"
            className="flex items-center justify-between rounded-lg border border-zinc-800 px-3 py-2 text-sm transition hover:border-zinc-700 hover:bg-zinc-800/40"
          >
            <span>
              <span className="font-medium text-zinc-200">{l.label}</span>
              <span className="ml-2 text-xs text-zinc-500">{l.blurb}</span>
            </span>
            <span className="text-zinc-500">↗</span>
          </a>
        ))}
      </CardBody>
    </Card>
  );
}
