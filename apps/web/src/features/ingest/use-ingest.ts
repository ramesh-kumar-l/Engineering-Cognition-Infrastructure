import { useMutation } from "@tanstack/react-query";
import { ingestDocument, ingestNote } from "./ingest.api";

/** Upload a document file (multipart). */
export function useIngestDocument() {
  return useMutation({ mutationKey: ["ingest-document"], mutationFn: ingestDocument });
}

/** Capture a free-text note. */
export function useIngestNote() {
  return useMutation({ mutationKey: ["ingest-note"], mutationFn: ingestNote });
}
