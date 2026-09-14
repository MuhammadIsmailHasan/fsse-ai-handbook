// See README.md.
export type MetricName = "LCP" | "INP" | "CLS" | "FCP" | "TTFB";
export type Rating = "good" | "needs-improvement" | "poor";

export const THRESHOLDS: Record<MetricName, readonly [number, number]> = { LCP: [0, 0], INP: [0, 0], CLS: [0, 0], FCP: [0, 0], TTFB: [0, 0] };

export function rateMetric(name: MetricName, value: number): Rating {
  return "good";
}

export function formatMetric(name: MetricName, value: number): string {
  return "";
}

export function p75(values: number[]): number | null {
  return null;
}

export function summarize(samples: { name: MetricName; value: number }[]): Partial<Record<MetricName, { p75: number; rating: Rating; count: number }>> {
  return {};
}
