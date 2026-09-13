// Personal data. See README.md.
export type Application = { id: number; role: string };

export async function getMyApplications(token: string): Promise<Application[]> {
  throw new Error("TODO");
}
