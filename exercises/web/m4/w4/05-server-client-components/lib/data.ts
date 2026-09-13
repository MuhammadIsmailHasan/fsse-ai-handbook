// Server-only data access. See README.md.
export type Job = { id: number; title: string; company: string; description: string; saved: boolean };

export async function getJob(id: number): Promise<Job | null> {
  throw new Error("TODO");
}
