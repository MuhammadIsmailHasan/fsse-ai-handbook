// Query key factory. See README.md.
import type { Filters } from "./api-types";

export const applicationKeys = {
  all: [] as unknown[],
  lists: (): unknown[] => [],
  list: (filters: Filters): unknown[] => [],
  detail: (id: number): unknown[] => [],
};
