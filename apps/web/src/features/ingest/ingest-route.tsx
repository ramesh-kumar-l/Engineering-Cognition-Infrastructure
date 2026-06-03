import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { DocumentIngestResult, NoteIngestResult } from "@/types/api";
import { DocumentForm } from "./components/document-form";
import { NoteForm } from "./components/note-form";
import { IngestResult } from "./components/ingest-result";

type LastResult =
  | { kind: "document"; result: DocumentIngestResult }
  | { kind: "note"; result: NoteIngestResult };

/** Ingest screen — capture documents and notes; provenance starts here. */
export function IngestRoute() {
  const [last, setLast] = useState<LastResult | null>(null);
  const navigate = useNavigate();

  return (
    <>
      <PageHeader
        title="Ingest"
        subtitle="Capture documents and notes. Every source is hashed, deduplicated, and stamped with its origin."
      />

      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Document</CardTitle>
          </CardHeader>
          <CardBody>
            <DocumentForm onIngested={(result) => setLast({ kind: "document", result })} />
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Note</CardTitle>
          </CardHeader>
          <CardBody>
            <NoteForm onIngested={(result) => setLast({ kind: "note", result })} />
          </CardBody>
        </Card>
      </div>

      {last && (
        <div className="mt-6">
          {last.kind === "document" ? (
            <IngestResult
              kindLabel="Document"
              id={last.result.id}
              contentHash={last.result.content_hash}
              source={last.result.source}
              deduplicated={last.result.deduplicated}
              ingestedAt={last.result.ingested_at}
              action={
                <Button
                  variant="outline"
                  onClick={() =>
                    navigate({ to: "/compress", search: { documentId: last.result.id } })
                  }
                >
                  Compress this document →
                </Button>
              }
            />
          ) : (
            <IngestResult
              kindLabel="Note"
              id={last.result.id}
              contentHash={last.result.content_hash}
              source={last.result.source}
              deduplicated={last.result.deduplicated}
              ingestedAt={last.result.ingested_at}
            />
          )}
        </div>
      )}
    </>
  );
}
