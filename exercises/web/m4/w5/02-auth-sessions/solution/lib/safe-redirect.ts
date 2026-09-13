const FALLBACK = "/dashboard";

export function safeNextPath(value: unknown): string {
  // Only same-site relative paths. "//evil.com" and "/\evil.com" are treated as absolute URLs by browsers.
  if (typeof value !== "string" || !/^\/(?![/\\])/.test(value)) return FALLBACK;
  return value;
}
