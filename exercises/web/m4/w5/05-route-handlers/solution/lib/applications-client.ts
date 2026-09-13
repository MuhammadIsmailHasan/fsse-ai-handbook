export class ApiError extends Error {
  constructor(public status: number, public code: string) {
    super(code);
  }
}

export type Application = { id: number; role: string; status: string };

async function request<T>(path: string, method: string, body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method,
    headers: body === undefined ? { Accept: "application/json" } : { Accept: "application/json", "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (response.status === 204) return null as T;
  const json = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, json?.error?.code ?? "unknown_error");
  return json as T;
}

export const applicationsClient = {
  list: (status?: string) => request<Application[]>(status ? `/api/applications?status=${encodeURIComponent(status)}` : "/api/applications", "GET"),
  create: (input: { company_id: number; role: string }) => request<Application>("/api/applications", "POST", input),
  update: (id: number, patch: Partial<Pick<Application, "role" | "status">>) => request<Application>(`/api/applications/${id}`, "PATCH", patch),
  remove: (id: number) => request<null>(`/api/applications/${id}`, "DELETE"),
};
