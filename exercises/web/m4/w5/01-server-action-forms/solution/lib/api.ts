// Provided: server-side call to the Flask API.
export class ApiError extends Error {
  constructor(public status: number, public code: string, public fields?: Record<string, string[]>) {
    super(code);
    this.name = "ApiError";
  }
}

export type NewApplication = { company_id: number; role: string; salary_min?: number; salary_max?: number };

export async function createApplication(input: NewApplication): Promise<{ id: number }> {
  const response = await fetch(`${process.env.API_URL}/api/v1/applications`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, body?.error?.code ?? "unknown_error", body?.error?.fields);
  return body.data;
}
