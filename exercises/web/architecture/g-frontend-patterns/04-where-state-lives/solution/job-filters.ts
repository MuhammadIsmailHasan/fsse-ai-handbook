export type JobFilters = { q: string; status: "open" | "closed" | "all"; remote: boolean; sort: "newest" | "salary"; page: number };
export const DEFAULT_FILTERS: JobFilters = { q: "", status: "open", remote: false, sort: "newest", page: 1 };

const STATUSES = ["open", "closed", "all"] as const;
const SORTS = ["newest", "salary"] as const;

function first(input: URLSearchParams | Record<string, string | string[] | undefined>, key: string): string | undefined {
  if (input instanceof URLSearchParams) return input.get(key) ?? undefined;
  const value = input[key];
  return Array.isArray(value) ? value[0] : value;
}

const oneOf = <T extends string>(options: readonly T[], value: string | undefined, fallback: T): T =>
  options.includes(value as T) ? (value as T) : fallback;

/** URL input is untrusted: every field is validated and falls back to its default. */
export function parseJobFilters(input: URLSearchParams | Record<string, string | string[] | undefined>): JobFilters {
  const page = Number(first(input, "page"));
  return {
    q: (first(input, "q") ?? "").trim().slice(0, 100),
    status: oneOf(STATUSES, first(input, "status"), DEFAULT_FILTERS.status),
    remote: first(input, "remote") === "1",
    sort: oneOf(SORTS, first(input, "sort"), DEFAULT_FILTERS.sort),
    page: Number.isInteger(page) && page >= 1 ? page : DEFAULT_FILTERS.page,
  };
}

/** Short, stable URLs: defaults are omitted and key order never changes. */
export function serializeJobFilters(filters: JobFilters): string {
  const params = new URLSearchParams();
  if (filters.q) params.set("q", filters.q);
  if (filters.status !== DEFAULT_FILTERS.status) params.set("status", filters.status);
  if (filters.remote) params.set("remote", "1");
  if (filters.sort !== DEFAULT_FILTERS.sort) params.set("sort", filters.sort);
  if (filters.page !== DEFAULT_FILTERS.page) params.set("page", String(filters.page));
  return params.toString();
}
