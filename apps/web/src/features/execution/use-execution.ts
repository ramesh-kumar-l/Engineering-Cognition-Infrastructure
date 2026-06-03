import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { StatusUpdateInput } from "@/types/api";
import {
  addTaskDependency,
  createGoal,
  createRoadmap,
  createTask,
  getGoalWhy,
  getTaskWhy,
  listGoals,
  listRoadmaps,
  listTasks,
  updateGoalStatus,
  updateTaskStatus,
} from "./execution.api";

// ── Roadmaps ────────────────────────────────────────────────────────────────
export function useRoadmaps() {
  return useQuery({ queryKey: ["roadmaps"], queryFn: listRoadmaps });
}

export function useCreateRoadmap() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createRoadmap,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["roadmaps"] }),
  });
}

// ── Goals ─────────────────────────────────────────────────────────────────--
export function useGoals(roadmapId: string | undefined) {
  return useQuery({
    queryKey: ["goals", roadmapId ?? null],
    queryFn: () => listGoals(roadmapId),
    enabled: Boolean(roadmapId),
  });
}

export function useCreateGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createGoal,
    onSuccess: (goal) => qc.invalidateQueries({ queryKey: ["goals", goal.roadmap_id ?? null] }),
  });
}

export function useUpdateGoalStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: StatusUpdateInput }) =>
      updateGoalStatus(id, input),
    onSuccess: (goal) => qc.invalidateQueries({ queryKey: ["goals", goal.roadmap_id ?? null] }),
  });
}

export function useGoalWhy(id: string | undefined, enabled: boolean) {
  return useQuery({
    queryKey: ["goal-why", id],
    queryFn: () => getGoalWhy(id!),
    enabled: Boolean(id) && enabled,
  });
}

// ── Tasks ─────────────────────────────────────────────────────────────────--
export function useTasks(goalId: string | undefined) {
  return useQuery({
    queryKey: ["tasks", goalId ?? null],
    queryFn: () => listTasks(goalId),
    enabled: Boolean(goalId),
  });
}

export function useCreateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createTask,
    onSuccess: (task) => qc.invalidateQueries({ queryKey: ["tasks", task.goal_id ?? null] }),
  });
}

export function useUpdateTaskStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: StatusUpdateInput }) =>
      updateTaskStatus(id, input),
    onSuccess: (task) => qc.invalidateQueries({ queryKey: ["tasks", task.goal_id ?? null] }),
  });
}

export function useAddTaskDependency(goalId: string | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, upstreamId }: { taskId: string; upstreamId: string }) =>
      addTaskDependency(taskId, upstreamId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks", goalId ?? null] }),
  });
}

export function useTaskWhy(id: string | undefined, enabled: boolean) {
  return useQuery({
    queryKey: ["task-why", id],
    queryFn: () => getTaskWhy(id!),
    enabled: Boolean(id) && enabled,
  });
}
