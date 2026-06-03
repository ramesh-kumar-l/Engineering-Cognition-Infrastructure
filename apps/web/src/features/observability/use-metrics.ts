import { useQuery } from "@tanstack/react-query";
import { getMetrics } from "./metrics.api";

/** Polls the Prometheus /metrics rollup for the Observability screen. */
export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: ({ signal }) => getMetrics(signal),
    refetchInterval: 15_000,
    staleTime: 10_000,
  });
}
