// Cached public data. See README.md.
import { cacheLife, cacheTag } from "next/cache";

export type Job = { id: number; title: string; company: string };

export async function getPublicJobs(): Promise<Job[]> {
  throw new Error("TODO");
}

export async function getJob(id: number): Promise<Job> {
  throw new Error("TODO");
}
