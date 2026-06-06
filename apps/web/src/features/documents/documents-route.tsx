import { Link } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardBody } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api-client";
import { useDocuments } from "./use-documents";

/** Documents screen — browse ingested sources and open one to read it. */
export function DocumentsRoute() {
  const docs = useDocuments();

  return (
    <>
      <PageHeader
        title="Documents"
        subtitle="Browse ingested sources. Open one to read its body, summaries, and structured mental model."
      />

      {docs.isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : docs.error ? (
        <Card>
          <CardBody className="text-sm text-danger">
            Could not load documents:{" "}
            {docs.error instanceof ApiError ? docs.error.detail : "Unexpected error"}
          </CardBody>
        </Card>
      ) : !docs.data || docs.data.length === 0 ? (
        <Card>
          <CardBody className="text-sm text-fg-muted">
            No documents yet. Ingest a file on the{" "}
            <Link to="/ingest" className="text-accent underline underline-offset-2">
              Ingest
            </Link>{" "}
            screen to get started.
          </CardBody>
        </Card>
      ) : (
        <ul className="space-y-2">
          {docs.data.map((doc) => (
            <li key={doc.id}>
              <Link
                to="/documents/$id"
                params={{ id: doc.id }}
                className="block rounded-xl border border-border bg-surface px-4 py-3 transition hover:border-border-strong hover:bg-surface-raised"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-fg">
                      {doc.title ?? "Untitled document"}
                    </div>
                    <div className="mt-0.5 truncate font-mono text-xs text-fg-subtle">
                      {doc.source}
                    </div>
                  </div>
                  <Badge tone="neutral">{doc.kind}</Badge>
                </div>
                {doc.tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {doc.tags.map((t) => (
                      <span
                        key={t}
                        className="rounded bg-surface-raised px-1.5 py-0.5 text-[11px] text-fg-muted"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
