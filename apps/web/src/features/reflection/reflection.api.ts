import { apiRequest } from "@/lib/api-client";
import {
  LessonListSchema,
  LessonSchema,
  RetrospectiveListSchema,
  RetrospectiveSchema,
  type CreateLessonInput,
  type CreateRetrospectiveInput,
  type Lesson,
  type Retrospective,
  type SupersedeLessonInput,
} from "@/types/api";

// ── Retrospectives ────────────────────────────────────────────────────────────
/** GET /retrospectives — all retrospectives. */
export function listRetrospectives(): Promise<Retrospective[]> {
  return apiRequest("/retrospectives", { schema: RetrospectiveListSchema });
}

/** POST /retrospectives — create and synchronously run a reflection cycle. */
export function createRetrospective(input: CreateRetrospectiveInput): Promise<Retrospective> {
  return apiRequest("/retrospectives", {
    method: "POST",
    body: input,
    schema: RetrospectiveSchema,
  });
}

// ── Lessons ───────────────────────────────────────────────────────────────--
/** GET /lessons?retrospective_id=&status= — lessons, optionally filtered. */
export function listLessons(filter: {
  retrospectiveId?: string;
  status?: string;
}): Promise<Lesson[]> {
  const params = new URLSearchParams();
  if (filter.retrospectiveId) params.set("retrospective_id", filter.retrospectiveId);
  if (filter.status) params.set("status", filter.status);
  const query = params.toString();
  return apiRequest(`/lessons${query ? `?${query}` : ""}`, { schema: LessonListSchema });
}

/** POST /lessons — manually record a lesson with optional evidence. */
export function createLesson(input: CreateLessonInput): Promise<Lesson> {
  return apiRequest("/lessons", { method: "POST", body: input, schema: LessonSchema });
}

/** POST /lessons/{id}/supersede — retire a lesson by replacing it with a newer claim. */
export function supersedeLesson(id: string, input: SupersedeLessonInput): Promise<Lesson> {
  return apiRequest(`/lessons/${id}/supersede`, {
    method: "POST",
    body: input,
    schema: LessonSchema,
  });
}
