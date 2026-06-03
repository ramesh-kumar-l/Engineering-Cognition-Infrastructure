import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Field } from "@/components/ui/field";
import { ApiError } from "@/lib/api-client";
import type { DocumentIngestResult, DocumentKind } from "@/types/api";
import { useIngestDocument } from "../use-ingest";

const KINDS: DocumentKind[] = ["markdown", "text", "pdf"];

/** Upload a document file → POST /documents. */
export function DocumentForm({ onIngested }: { onIngested: (r: DocumentIngestResult) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [kind, setKind] = useState<DocumentKind>("markdown");
  const [source, setSource] = useState("");
  const [title, setTitle] = useState("");
  const [tags, setTags] = useState("");
  const ingest = useIngestDocument();

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file || !source.trim()) return;
    ingest.mutate(
      {
        file,
        kind,
        source: source.trim(),
        title: title.trim() || undefined,
        tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      },
      { onSuccess: onIngested },
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Field label="File" hint="markdown, plain text, or PDF">
        <input
          type="file"
          accept=".md,.markdown,.txt,.pdf,text/markdown,text/plain,application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="block w-full text-sm text-zinc-400 file:mr-3 file:rounded-md file:border-0 file:bg-zinc-800 file:px-3 file:py-1.5 file:text-sm file:text-zinc-200 hover:file:bg-zinc-700"
        />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Kind">
          <Select value={kind} onChange={(e) => setKind(e.target.value as DocumentKind)} className="w-full">
            {KINDS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Source" hint="provenance origin, e.g. repo://adr-006">
          <Input value={source} onChange={(e) => setSource(e.target.value)} placeholder="repo://…" />
        </Field>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Title (optional)">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="ADR-006" />
        </Field>
        <Field label="Tags (optional)" hint="comma-separated">
          <Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="retrieval, adr" />
        </Field>
      </div>
      {ingest.error && (
        <p className="text-sm text-red-300">
          Upload failed: {ingest.error instanceof ApiError ? ingest.error.detail : "Unexpected error"}
        </p>
      )}
      <Button type="submit" disabled={ingest.isPending || !file || !source.trim()}>
        {ingest.isPending ? "Uploading…" : "Ingest document"}
      </Button>
    </form>
  );
}
