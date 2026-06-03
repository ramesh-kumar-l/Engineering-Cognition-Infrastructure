import { apiRequest } from "@/lib/api-client";
import {
  DocumentIngestResultSchema,
  NoteIngestResultSchema,
  type DocumentIngestResult,
  type DocumentKind,
  type NoteIngestRequest,
  type NoteIngestResult,
} from "@/types/api";

export interface DocumentIngestInput {
  file: File;
  kind: DocumentKind;
  source: string;
  title?: string;
  author?: string;
  tags?: string[];
}

/** POST /documents (multipart). Backend dedups on content hash. */
export function ingestDocument(input: DocumentIngestInput): Promise<DocumentIngestResult> {
  const form = new FormData();
  form.append("file", input.file);
  form.append("kind", input.kind);
  form.append("source", input.source);
  if (input.title) form.append("title", input.title);
  if (input.author) form.append("author", input.author);
  if (input.tags?.length) form.append("tags", input.tags.join(","));
  return apiRequest("/documents", { method: "POST", body: form, schema: DocumentIngestResultSchema });
}

/** POST /notes (JSON). */
export function ingestNote(input: NoteIngestRequest): Promise<NoteIngestResult> {
  return apiRequest("/notes", {
    method: "POST",
    body: {
      body: input.body,
      source: input.source,
      author: input.author,
      tags: input.tags ?? [],
    },
    schema: NoteIngestResultSchema,
  });
}
