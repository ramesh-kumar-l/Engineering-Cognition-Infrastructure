import { useMutation } from "@tanstack/react-query";
import { searchMemory } from "./search.api";
import type { SearchRequest } from "@/types/api";

/** Runs a search on submit, exposing loading/error/data for the results view. */
export function useSearch() {
  return useMutation({
    mutationKey: ["retrieval-search"],
    mutationFn: (req: SearchRequest) => searchMemory(req),
  });
}
