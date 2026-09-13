// Provided: fake data access. In CareerPilot this would call the Flask API.
export type Job = { id: number; title: string; company: string; city: string };

const JOBS: Job[] = [
  { id: 1, title: "Backend Engineer", company: "Kopi Data", city: "Jakarta" },
  { id: 2, title: "AI Engineer", company: "Lintas AI", city: "Remote" },
];

export async function getJobs(): Promise<Job[]> {
  return JOBS;
}

export async function getJob(id: number): Promise<Job | null> {
  return JOBS.find((job) => job.id === id) ?? null;
}
