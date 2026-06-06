import { useQuery } from "@tanstack/react-query";
import { getDocument, getNote, listDocuments } from "./documents.api";

/** Browse list of documents. */
export function useDocuments() {
  return useQuery({ queryKey: ["documents"], queryFn: listDocuments });
}

/** A single document; only fetched once an id is present. */
export function useDocument(id: string | undefined) {
  return useQuery({
    queryKey: ["document", id],
    queryFn: () => getDocument(id!),
    enabled: Boolean(id),
  });
}

/** A single note; only fetched once an id is present. */
export function useNote(id: string | undefined) {
  return useQuery({
    queryKey: ["note", id],
    queryFn: () => getNote(id!),
    enabled: Boolean(id),
  });
}
