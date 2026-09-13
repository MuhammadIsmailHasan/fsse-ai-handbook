import "server-only"; // importing this file from a Client Component becomes a build error

export type Job = { id: number; title: string; company: string; description: string; saved: boolean };

export async function getJob(id: number): Promise<Job | null> {
  const response = await fetch(`${process.env.API_URL}/api/v1/jobs/${id}`, {
    headers: { Authorization: `Bearer ${process.env.API_TOKEN}` }, // the token never leaves the server
  });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`Failed to load job ${id}: ${response.status}`);
  return ((await response.json()) as { data: Job }).data;
}
