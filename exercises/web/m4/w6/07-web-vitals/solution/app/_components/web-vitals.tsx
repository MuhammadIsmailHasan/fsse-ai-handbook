"use client";

import { useReportWebVitals } from "next/web-vitals";

type Metric = { name: string; value: number; rating: string; id: string; navigationType: string };

// Module-level function → stable reference → each metric is reported once.
export function reportWebVital(metric: Metric): void {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    id: metric.id,
    navigationType: metric.navigationType,
    path: window.location.pathname,
  });
  if (typeof navigator.sendBeacon === "function") {
    navigator.sendBeacon("/api/vitals", body); // still delivered when the tab is closing
  } else {
    void fetch("/api/vitals", { method: "POST", body, keepalive: true, headers: { "Content-Type": "application/json" } });
  }
}

export function WebVitals() {
  useReportWebVitals(reportWebVital);
  return null;
}
