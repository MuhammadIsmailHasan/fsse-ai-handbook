export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";
export type Application = { id: number; role: string; status: Status; company: { id: number; name: string } };
export type ApplicationList = { data: Application[]; meta: { page: number; per_page: number; total: number } };

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly fields?: Record<string, string[]>,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ErrorBody = { error?: { code?: unknown; message?: unknown; fields?: Record<string, string[]> } };

export function createApiClient({ baseUrl, getToken, fetchImpl = fetch }: { baseUrl: string; getToken: () => string | undefined; fetchImpl?: typeof fetch }) {
  async function request<T>(path: string, query: Record<string, string | number | undefined> = {}): Promise<T> {
    const url = new URL(path, baseUrl);
    for (const [key, value] of Object.entries(query)) if (value !== undefined) url.searchParams.set(key, String(value));

    const token = getToken();
    let response: Response;
    try {
      response = await fetchImpl(url.toString(), {
        headers: { Accept: "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        cache: "no-store", // personal data: never cache across users
      });
    } catch {
      throw new ApiError(0, "network_error", "Could not reach the CareerPilot API");
    }

    const body: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      const error = (body as ErrorBody | null)?.error;
      const code = typeof error?.code === "string" ? error.code : "unknown_error";
      const message = typeof error?.message === "string" ? error.message : `Request failed with status ${response.status}`;
      throw new ApiError(response.status, code, message, error?.fields);
    }
    return body as T;
  }

  return {
    listApplications: (filters: { status?: Status; page?: number } = {}) =>
      request<ApplicationList>("/api/v1/applications", { status: filters.status, page: filters.page }),
    getApplication: async (id: number) => (await request<{ data: Application }>(`/api/v1/applications/${id}`)).data,
  };
}
