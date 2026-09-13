// Presentational React components. See README.md.
import type { ReactNode } from "react";

export type Job = { id: number; title: string; company: string; city: string; salaryMax: number | null; skills: string[] };

export function PageHeader(props: { title: string; subtitle?: string }) {
  return null;
}

export function JobCard(props: { job: Job }) {
  return null;
}

export function EmptyState(props: { message: string; children?: ReactNode }) {
  return null;
}

export function JobList(props: { jobs: Job[] }) {
  return null;
}

export function JobsPage(props: { jobs: Job[] }) {
  return null;
}
