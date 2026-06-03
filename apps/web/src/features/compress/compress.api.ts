import { apiRequest } from "@/lib/api-client";
import {
  CompressResponseSchema,
  EmbedResponseSchema,
  MentalModelSchema,
  SummaryListSchema,
  type CompressResponse,
  type EmbedResponse,
  type MentalModel,
  type Summary,
} from "@/types/api";

/** POST /compress/documents/{id} — run the summarization + mental-model pipeline. */
export function compressDocument(documentId: string): Promise<CompressResponse> {
  return apiRequest(`/compress/documents/${documentId}`, {
    method: "POST",
    schema: CompressResponseSchema,
  });
}

/** GET /compress/documents/{id}/summaries — the three summary levels. */
export function getDocumentSummaries(documentId: string): Promise<Summary[]> {
  return apiRequest(`/compress/documents/${documentId}/summaries`, { schema: SummaryListSchema });
}

/** GET /compress/documents/{id}/mental-model — 404 when not yet compressed. */
export function getDocumentMentalModel(documentId: string): Promise<MentalModel> {
  return apiRequest(`/compress/documents/${documentId}/mental-model`, { schema: MentalModelSchema });
}

/** POST /retrieval/embed/documents/{id} — make the document searchable. */
export function embedDocument(documentId: string): Promise<EmbedResponse> {
  return apiRequest(`/retrieval/embed/documents/${documentId}`, {
    method: "POST",
    schema: EmbedResponseSchema,
  });
}
