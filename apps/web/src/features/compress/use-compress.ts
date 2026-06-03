import { useMutation, useQuery } from "@tanstack/react-query";
import {
  compressDocument,
  embedDocument,
  getDocumentMentalModel,
  getDocumentSummaries,
} from "./compress.api";

/** Trigger the compression pipeline for a document. */
export function useCompressDocument() {
  return useMutation({ mutationKey: ["compress-document"], mutationFn: compressDocument });
}

/** Make a document searchable via embeddings. */
export function useEmbedDocument() {
  return useMutation({ mutationKey: ["embed-document"], mutationFn: embedDocument });
}

/** Summaries for a document; only fetched once an id is present. */
export function useDocumentSummaries(documentId: string | undefined) {
  return useQuery({
    queryKey: ["document-summaries", documentId],
    queryFn: () => getDocumentSummaries(documentId!),
    enabled: Boolean(documentId),
  });
}

/** Mental model for a document; 404 means "not compressed yet" (handled in UI). */
export function useDocumentMentalModel(documentId: string | undefined) {
  return useQuery({
    queryKey: ["document-mental-model", documentId],
    queryFn: () => getDocumentMentalModel(documentId!),
    enabled: Boolean(documentId),
  });
}
