import { QueryClient } from "@tanstack/react-query";
import { ApiError } from "./api-client";

/** Shared query client; do not retry auth/client errors, only transient ones. */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) => {
        if (error instanceof ApiError && error.status < 500) return false;
        return failureCount < 2;
      },
    },
  },
});
