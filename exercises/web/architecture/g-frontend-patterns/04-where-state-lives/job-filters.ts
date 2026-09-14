// See README.md.
export type JobFilters = { q: string; status: "open" | "closed" | "all"; remote: boolean; sort: "newest" | "salary"; page: number };
export const DEFAULT_FILTERS: JobFilters = { q: "", status: "open", remote: false, sort: "newest", page: 1 };

export function parseJobFilters(input: URLSearchParams | Record<string, string | string[] | undefined>): JobFilters {
  return DEFAULT_FILTERS;
}

export function serializeJobFilters(filters: JobFilters): string {
  return "";
}
