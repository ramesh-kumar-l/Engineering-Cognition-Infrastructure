import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Field } from "@/components/ui/field";
import { ApiError } from "@/lib/api-client";
import type { NoteIngestResult } from "@/types/api";
import { useIngestNote } from "../use-ingest";

/** Capture a free-text note → POST /notes. */
export function NoteForm({ onIngested }: { onIngested: (r: NoteIngestResult) => void }) {
  const [body, setBody] = useState("");
  const [source, setSource] = useState("");
  const [tags, setTags] = useState("");
  const ingest = useIngestNote();

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!body.trim() || !source.trim()) return;
    ingest.mutate(
      {
        body: body.trim(),
        source: source.trim(),
        tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      },
      { onSuccess: onIngested },
    );
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <Field label="Note">
        <Textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Capture a decision, observation, or insight…"
        />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Source" hint="provenance origin">
          <Input value={source} onChange={(e) => setSource(e.target.value)} placeholder="meeting://…" />
        </Field>
        <Field label="Tags (optional)" hint="comma-separated">
          <Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="decision, infra" />
        </Field>
      </div>
      {ingest.error && (
        <p className="text-sm text-red-300">
          Capture failed: {ingest.error instanceof ApiError ? ingest.error.detail : "Unexpected error"}
        </p>
      )}
      <Button type="submit" disabled={ingest.isPending || !body.trim() || !source.trim()}>
        {ingest.isPending ? "Saving…" : "Capture note"}
      </Button>
    </form>
  );
}
