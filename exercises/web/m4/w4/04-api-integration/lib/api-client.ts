// Typed API client for the CareerPilot Flask API. See README.md.
export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";
export type Application = { id: number; role: string; status: Status; company: { id: number; name: string } };
export type ApplicationList = { data: Application[]; meta: { page: number; per_page: number; total: number } };

export class ApiError extends Error {}

export function createApiClient(options: { baseUrl: string; getToken: () => string | undefined; fetchImpl?: typeof fetch }) {
  return {
    listApplications: async (filters: { status?: Status; page?: number } = {}): Promise<ApplicationList> => {
      throw new Error("TODO");
    },
    getApplication: async (id: number): Promise<Application> => {
      throw new Error("TODO");
    },
  };
}
