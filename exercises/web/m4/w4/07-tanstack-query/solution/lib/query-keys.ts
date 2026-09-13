import type { Filters } from "./api-types";

// One place that knows the shape of every key → invalidation by prefix is reliable.
export const applicationKeys = {
  all: ["applications"] as const,
  lists: () => [...applicationKeys.all, "list"] as const,
  list: (filters: Filters) => [...applicationKeys.lists(), filters] as const,
  detail: (id: number) => [...applicationKeys.all, "detail", id] as const,
};
