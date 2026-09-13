import { cacheLife, cacheTag } from "next/cache";

export type Job = { id: number; title: string; company: string };

// Same for every visitor → safe to cache. Tagged so a mutation can expire it on demand.
export async function getPublicJobs(): Promise<Job[]> {
  "use cache";
  cacheLife("hours");
  cacheTag("jobs");
  const response = await fetch(`${process.env.API_URL}/api/v1/jobs`);
  if (!response.ok) throw new Error(`Failed to load jobs: ${response.status}`);
  return ((await response.json()) as { data: Job[] }).data;
}

export async function getJob(id: number): Promise<Job> {
  "use cache";
  cacheLife("hours");
  cacheTag("jobs", `job-${id}`); // `id` is an argument, so it's part of the cache key too
  const response = await fetch(`${process.env.API_URL}/api/v1/jobs/${id}`);
  if (!response.ok) throw new Error(`Failed to load job ${id}: ${response.status}`);
  return ((await response.json()) as { data: Job }).data;
}
