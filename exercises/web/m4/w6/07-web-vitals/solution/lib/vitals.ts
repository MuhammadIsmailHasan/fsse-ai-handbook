export type MetricName = "LCP" | "INP" | "CLS" | "FCP" | "TTFB";
export type Rating = "good" | "needs-improvement" | "poor";

// web.dev thresholds: [good upper bound, needs-improvement upper bound]
export const THRESHOLDS: Record<MetricName, readonly [number, number]> = {
  LCP: [2500, 4000],
  INP: [200, 500],
  CLS: [0.1, 0.25],
  FCP: [1800, 3000],
  TTFB: [800, 1800],
};

export function rateMetric(name: MetricName, value: number): Rating {
  const [good, needsImprovement] = THRESHOLDS[name];
  if (value <= good) return "good";
  return value <= needsImprovement ? "needs-improvement" : "poor";
}

export function formatMetric(name: MetricName, value: number): string {
  return name === "CLS" ? value.toFixed(2) : `${Math.round(value)} ms`;
}

export function p75(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = values.toSorted((a, b) => a - b);
  return sorted[Math.ceil(0.75 * sorted.length) - 1]!;
}

export function summarize(samples: { name: MetricName; value: number }[]) {
  const byName = new Map<MetricName, number[]>();
  for (const { name, value } of samples) byName.set(name, [...(byName.get(name) ?? []), value]);

  const summary: Partial<Record<MetricName, { p75: number; rating: Rating; count: number }>> = {};
  for (const [name, values] of byName) {
    const value = p75(values)!;
    summary[name] = { p75: value, rating: rateMetric(name, value), count: values.length };
  }
  return summary;
}
