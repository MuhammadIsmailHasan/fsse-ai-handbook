// State and events. See README.md.
import { useState } from "react";

export type JobSummary = { id: number; title: string };

export function SaveButton(props: { saved: boolean; onToggle: () => void; jobTitle: string }) {
  return null;
}

export function SavedJobsBoard(props: { jobs: JobSummary[] }) {
  return null;
}

export function ApplicationCounter() {
  return null;
}
