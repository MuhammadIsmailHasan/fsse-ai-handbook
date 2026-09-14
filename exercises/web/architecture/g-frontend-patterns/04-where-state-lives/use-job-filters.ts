"use client";
// See README.md.
import { DEFAULT_FILTERS, type JobFilters } from "./job-filters";

export function useJobFilters(): { filters: JobFilters; setFilters: (patch: Partial<JobFilters>, options?: { history?: "push" | "replace" }) => void } {
  return { filters: DEFAULT_FILTERS, setFilters: () => {} };
}
