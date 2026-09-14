"use client";

import dynamic from "next/dynamic";

// ssr: false is only allowed inside Client Components.
export const SalaryChartLazy = dynamic(() => import("./salary-chart"), {
  ssr: false,
  loading: () => <p>Loading salary chart…</p>,
});
