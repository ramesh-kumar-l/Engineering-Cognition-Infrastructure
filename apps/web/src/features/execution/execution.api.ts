import { apiRequest } from "@/lib/api-client";
import {
  GoalListSchema,
  GoalSchema,
  RoadmapListSchema,
  RoadmapSchema,
  TaskListSchema,
  TaskSchema,
  WhyListSchema,
  type Citation,
  type CreateGoalInput,
  type CreateRoadmapInput,
  type CreateTaskInput,
  type Goal,
  type Roadmap,
  type StatusUpdateInput,
  type Task,
} from "@/types/api";

// ── Roadmaps ────────────────────────────────────────────────────────────────
/** GET /roadmaps — all roadmaps for the current tenant. */
export function listRoadmaps(): Promise<Roadmap[]> {
  return apiRequest("/roadmaps", { schema: RoadmapListSchema });
}

/** POST /roadmaps — create a roadmap. */
export function createRoadmap(input: CreateRoadmapInput): Promise<Roadmap> {
  return apiRequest("/roadmaps", { method: "POST", body: input, schema: RoadmapSchema });
}

// ── Goals ─────────────────────────────────────────────────────────────────--
/** GET /goals?roadmap_id= — goals, optionally scoped to one roadmap. */
export function listGoals(roadmapId: string | undefined): Promise<Goal[]> {
  const query = roadmapId ? `?roadmap_id=${encodeURIComponent(roadmapId)}` : "";
  return apiRequest(`/goals${query}`, { schema: GoalListSchema });
}

/** POST /goals — create a goal (citations carried from Search land here later). */
export function createGoal(input: CreateGoalInput): Promise<Goal> {
  return apiRequest("/goals", { method: "POST", body: input, schema: GoalSchema });
}

/** PATCH /goals/{id}/status — transition a goal's status. */
export function updateGoalStatus(id: string, input: StatusUpdateInput): Promise<Goal> {
  return apiRequest(`/goals/${id}/status`, { method: "PATCH", body: input, schema: GoalSchema });
}

/** GET /goals/{id}/why — stored citations justifying the goal. */
export function getGoalWhy(id: string): Promise<Citation[]> {
  return apiRequest(`/goals/${id}/why`, { schema: WhyListSchema });
}

// ── Tasks ─────────────────────────────────────────────────────────────────--
/** GET /tasks?goal_id= — tasks, optionally scoped to one goal. */
export function listTasks(goalId: string | undefined): Promise<Task[]> {
  const query = goalId ? `?goal_id=${encodeURIComponent(goalId)}` : "";
  return apiRequest(`/tasks${query}`, { schema: TaskListSchema });
}

/** POST /tasks — create a task under a goal. */
export function createTask(input: CreateTaskInput): Promise<Task> {
  return apiRequest("/tasks", { method: "POST", body: input, schema: TaskSchema });
}

/** PATCH /tasks/{id}/status — transition a task's status. */
export function updateTaskStatus(id: string, input: StatusUpdateInput): Promise<Task> {
  return apiRequest(`/tasks/${id}/status`, { method: "PATCH", body: input, schema: TaskSchema });
}

/** POST /tasks/{id}/dependencies — upstream must complete before this task (204). */
export function addTaskDependency(taskId: string, upstreamId: string): Promise<void> {
  return apiRequest(`/tasks/${taskId}/dependencies`, {
    method: "POST",
    body: { upstream_id: upstreamId },
  });
}

/** GET /tasks/{id}/why — stored citations justifying the task. */
export function getTaskWhy(id: string): Promise<Citation[]> {
  return apiRequest(`/tasks/${id}/why`, { schema: WhyListSchema });
}
