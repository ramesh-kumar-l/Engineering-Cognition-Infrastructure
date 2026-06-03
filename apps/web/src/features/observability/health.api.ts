import { apiRequest } from "@/lib/api-client";
import { HealthSchema, type Health } from "@/types/api";

export function getHealth(signal?: AbortSignal): Promise<Health> {
  return apiRequest("/healthz", { schema: HealthSchema, signal });
}
