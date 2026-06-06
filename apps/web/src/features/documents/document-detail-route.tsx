import { Link, getRouteApi } from "@tanstack/react-router";
import { Card, CardBody } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, type TabItem } from "@/components/ui/tabs";
import { Markdown } from "@/components/ui/markdown";
import { ApiError } from "@/lib/api-client";
import { useDocumentMentalModel, useDocumentSummaries } from "@/features/compress/use-compress";
import { SummaryList } from "@/features/compress/components/summary-list";
import { MentalModelView } from "@/features/compress/components/mental-model-view";
import { useDocument } from "./use-documents";

const route = getRouteApi("/documents/$id");

/** Document viewer — body + provenance metadata + compressed artifacts. */
export function DocumentDetailRoute() {
  const { id } = route.useParams();
  const doc = useDocument(id);

  return (
    <>
      <Link to="/documents" className="text-sm text-fg-muted hover:text-fg">
        ← All documents
      </Link>

      {doc.isLoading ? (
        <div className="mt-4 space-y-3">
          <Skeleton className="h-8 w-2/3" />
          <Skeleton className="h-40 w-full" />
        </div>
      ) : doc.error ? (
        <Card className="mt-4">
          <CardBody className="text-sm text-danger">
            {doc.error instanceof ApiError && doc.error.status === 404
              ? "Document not found (it may belong to another tenant)."
              : `Could not load document: ${
                  doc.error instanceof ApiError ? doc.error.detail : "Unexpected error"
                }`}
          </CardBody>
        </Card>
      ) : doc.data ? (
        <Viewer id={id} doc={doc.data} />
      ) : null}
    </>
  );
}

function Viewer({ id, doc }: { id: string; doc: NonNullable<ReturnType<typeof useDocument>["data"]> }) {
  const summaries = useDocumentSummaries(id);
  const mentalModel = useDocumentMentalModel(id);

  const tabs: TabItem[] = [
    {
      id: "body",
      label: "Document",
      content:
        doc.kind === "markdown" ? (
          <Markdown text={doc.body} />
        ) : (
          <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-fg">
            {doc.body}
          </pre>
        ),
    },
    {
      id: "summaries",
      label: "Summaries",
      count: summaries.data?.length,
      content: summaries.isLoading ? (
        <Skeleton className="h-24 w-full" />
      ) : summaries.error ? (
        <Note>Could not load summaries.</Note>
      ) : (summaries.data?.length ?? 0) === 0 ? (
        <Note>
          Not compressed yet.{" "}
          <Link
            to="/compress"
            search={{ documentId: id }}
            className="text-accent underline underline-offset-2"
          >
            Run compression
          </Link>
          .
        </Note>
      ) : (
        <SummaryList summaries={summaries.data ?? []} />
      ),
    },
    {
      id: "mental-model",
      label: "Mental model",
      content: mentalModel.isLoading ? (
        <Skeleton className="h-24 w-full" />
      ) : mentalModel.error instanceof ApiError && mentalModel.error.status === 404 ? (
        <Note>No mental model yet. Run compression to build it.</Note>
      ) : mentalModel.error ? (
        <Note>Could not load the mental model.</Note>
      ) : mentalModel.data ? (
        <MentalModelView model={mentalModel.data} />
      ) : null,
    },
  ];

  return (
    <div className="mt-3 space-y-5">
      <header className="space-y-2">
        <div className="flex items-start justify-between gap-3">
          <h1 className="text-xl font-semibold tracking-tight text-fg">
            {doc.title ?? "Untitled document"}
          </h1>
          <div className="flex shrink-0 gap-2">
            <Badge tone="neutral">{doc.kind}</Badge>
            <Link to="/compress" search={{ documentId: id }}>
              <Button variant="outline" className="py-1 text-xs">
                Compress & embed
              </Button>
            </Link>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-fg-subtle">
          <span className="truncate">{doc.source}</span>
          {doc.author && <span>by {doc.author}</span>}
          <span>ingested {formatDate(doc.ingested_at)}</span>
          <span>hash {doc.content_hash.slice(0, 12)}</span>
        </div>
        {doc.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
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
      </header>

      <Card>
        <CardBody>
          <Tabs items={tabs} />
        </CardBody>
      </Card>
    </div>
  );
}

function Note({ children }: { children: React.ReactNode }) {
  return <p className="text-sm text-fg-muted">{children}</p>;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}
