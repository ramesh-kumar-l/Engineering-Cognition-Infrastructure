import { useQuery } from "@tanstack/react-query";
import { getHealth, getReadyz } from "./health.api";

/** Polls backend liveness; drives the top-bar health pill. */
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => getHealth(signal),
    refetchInterval: 15_000,
    staleTime: 10_000,
  });
}

/** Polls backend readiness (DB reachable) for the Observability screen. */
export function useReadiness() {
  return useQuery({
    queryKey: ["readyz"],
    queryFn: ({ signal }) => getReadyz(signal),
    refetchInterval: 15_000,
    staleTime: 10_000,
  });
}
