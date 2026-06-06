import { apiRequest } from "@/lib/api-client";
import {
  DocumentDetailSchema,
  DocumentListSchema,
  NoteDetailSchema,
  type DocumentDetail,
  type DocumentListItem,
  type NoteDetail,
} from "@/types/api";

/** GET /documents — browse list for the current tenant. */
export function listDocuments(): Promise<DocumentListItem[]> {
  return apiRequest("/documents", { schema: DocumentListSchema });
}

/** GET /documents/{id} — full document for the viewer. */
export function getDocument(id: string): Promise<DocumentDetail> {
  return apiRequest(`/documents/${id}`, { schema: DocumentDetailSchema });
}

/** GET /notes/{id} — full note (search citations may resolve to notes). */
export function getNote(id: string): Promise<NoteDetail> {
  return apiRequest(`/notes/${id}`, { schema: NoteDetailSchema });
}
