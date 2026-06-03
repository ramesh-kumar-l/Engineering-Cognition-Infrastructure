import { useState, type FormEvent } from "react";
import { getRouteApi, useNavigate } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Field } from "@/components/ui/field";
import { ApiError } from "@/lib/api-client";
import {
  useCompressDocument,
  useDocumentMentalModel,
  useDocumentSummaries,
} from "./use-compress";
import { SummaryList } from "./components/summary-list";
import { MentalModelView } from "./components/mental-model-view";
import { EmbedPanel } from "./components/embed-panel";

const route = getRouteApi("/compress");

/** Compress screen — distill a document into summaries + a mental model, then embed it. */
export function CompressRoute() {
  const { documentId } = route.useSearch();
  const navigate = useNavigate();
  const [docId, setDocId] = useState(documentId ?? "");

  const activeId = documentId?.trim() || undefined;
  const compress = useCompressDocument();
  const summaries = useDocumentSummaries(activeId);
  const mentalModel = useDocumentMentalModel(activeId);

  function onLoad(e: FormEvent) {
    e.preventDefault();
    const id = docId.trim();
    if (id) navigate({ to: "/compress", search: { documentId: id } });
  }

  function onCompress() {
    if (!activeId) return;
    compress.mutate(activeId, {
      onSuccess: () => {
        summaries.refetch();
        mentalModel.refetch();
      },
    });
  }

  return (
    <>
      <PageHeader
        title="Compress"
        subtitle="Distill an ingested document into layered summaries and a structured mental model — then make it searchable."
      />

      <Card className="mb-6">
        <CardBody>
          <form onSubmit={onLoad} className="flex items-end gap-3">
            <div className="flex-1">
              <Field label="Document ID" hint="from an ingested document (carried over from Ingest)">
                <Input
                  value={docId}
                  onChange={(e) => setDocId(e.target.value)}
                  placeholder="00000000-0000-0000-0000-000000000000"
                  className="font-mono"
                />
              </Field>
            </div>
            <Button type="submit" variant="outline" disabled={!docId.trim()}>
              Load
            </Button>
            <Button type="button" onClick={onCompress} disabled={!activeId || compress.isPending}>
              {compress.isPending ? "Compressing…" : "Run compression"}
            </Button>
          </form>
          {compress.isSuccess && (
            <p className="mt-3 flex items-center gap-2 text-sm text-zinc-400">
              <Badge tone="good">{compress.data.summaries_created} summaries</Badge>
              {compress.data.has_mental_model && <Badge tone="info">mental model</Badge>}
              {compress.data.has_playbook && <Badge tone="info">playbook</Badge>}
            </p>
          )}
          {compress.error && (
            <p className="mt-3 text-sm text-red-300">
              Compression failed:{" "}
              {compress.error instanceof ApiError ? compress.error.detail : "Unexpected error"}
              {compress.error instanceof ApiError && compress.error.status >= 500
                ? " — the LLM provider (Ollama) may be unavailable."
                : ""}
            </p>
          )}
        </CardBody>
      </Card>

      {!activeId ? (
        <Card>
          <CardBody className="text-sm text-zinc-400">
            Enter a document ID above, or ingest a document and choose “Compress this document”.
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-6">
          <EmbedPanel documentId={activeId} />

          <section className="space-y-3">
            <h2 className="text-sm font-semibold tracking-tight text-zinc-200">Summaries</h2>
            {summaries.isLoading ? (
              <Loading />
            ) : summaries.error ? (
              <ErrorCard error={summaries.error} fallback="Could not load summaries." />
            ) : (
              <SummaryList summaries={summaries.data ?? []} />
            )}
          </section>

          <section className="space-y-3">
            <h2 className="text-sm font-semibold tracking-tight text-zinc-200">Mental model</h2>
            {mentalModel.isLoading ? (
              <Loading />
            ) : mentalModel.error instanceof ApiError && mentalModel.error.status === 404 ? (
              <Card>
                <CardBody className="text-sm text-zinc-400">
                  No mental model yet. Run compression to build it.
                </CardBody>
              </Card>
            ) : mentalModel.error ? (
              <ErrorCard error={mentalModel.error} fallback="Could not load the mental model." />
            ) : mentalModel.data ? (
              <MentalModelView model={mentalModel.data} />
            ) : null}
          </section>
        </div>
      )}
    </>
  );
}

function Loading() {
  return (
    <Card>
      <CardBody className="text-sm text-zinc-400">Loading…</CardBody>
    </Card>
  );
}

function ErrorCard({ error, fallback }: { error: unknown; fallback: string }) {
  const detail = error instanceof ApiError ? error.detail : fallback;
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-red-300">Error</CardTitle>
      </CardHeader>
      <CardBody className="text-sm text-red-300">{detail}</CardBody>
    </Card>
  );
}
