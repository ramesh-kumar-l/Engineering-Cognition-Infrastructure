import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { SupersedeLessonInput } from "@/types/api";
import {
  createLesson,
  createRetrospective,
  listLessons,
  listRetrospectives,
  supersedeLesson,
} from "./reflection.api";

// ── Retrospectives ────────────────────────────────────────────────────────────
export function useRetrospectives() {
  return useQuery({ queryKey: ["retrospectives"], queryFn: listRetrospectives });
}

export function useCreateRetrospective() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createRetrospective,
    onSuccess: () => {
      // A run can mint lessons, so refresh both surfaces.
      qc.invalidateQueries({ queryKey: ["retrospectives"] });
      qc.invalidateQueries({ queryKey: ["lessons"] });
    },
  });
}

// ── Lessons ───────────────────────────────────────────────────────────────--
export function useLessons(filter: { retrospectiveId?: string; status?: string }) {
  return useQuery({
    queryKey: ["lessons", filter.retrospectiveId ?? null, filter.status ?? null],
    queryFn: () => listLessons(filter),
  });
}

export function useCreateLesson() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createLesson,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lessons"] }),
  });
}

export function useSupersedeLesson() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: SupersedeLessonInput }) =>
      supersedeLesson(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["lessons"] }),
  });
}
