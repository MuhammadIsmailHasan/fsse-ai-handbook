export type Application = { id: number; role: string };

// Personal data: never cached, so one user's applications can't be served to another.
export async function getMyApplications(token: string): Promise<Application[]> {
  const response = await fetch(`${process.env.API_URL}/api/v1/applications`, { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) throw new Error(`Failed to load applications: ${response.status}`);
  return ((await response.json()) as { data: Application[] }).data;
}
