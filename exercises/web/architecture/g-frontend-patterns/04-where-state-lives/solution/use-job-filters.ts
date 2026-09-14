"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";
import { parseJobFilters, serializeJobFilters, type JobFilters } from "./job-filters";

export function useJobFilters() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const current = searchParams.toString();
  const filters = useMemo(() => parseJobFilters(new URLSearchParams(current)), [current]);

  function setFilters(patch: Partial<JobFilters>, { history = "push" }: { history?: "push" | "replace" } = {}) {
    const changesOtherThanPage = Object.keys(patch).some((key) => key !== "page");
    const next: JobFilters = { ...filters, ...patch, ...(changesOtherThanPage && !("page" in patch) ? { page: 1 } : {}) };
    const query = serializeJobFilters(next);
    if (query === serializeJobFilters(filters)) return;
    const href = query ? `${pathname}?${query}` : pathname;
    router[history](href, { scroll: false });
  }

  return { filters, setFilters };
}
