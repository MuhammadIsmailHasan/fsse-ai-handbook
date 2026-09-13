// Provided.
export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";
export type Application = { id: number; role: string; status: Status };
export type Filters = { status?: Status; q?: string };

export interface ApplicationsApi {
  listApplications(filters: Filters, options?: { signal?: AbortSignal }): Promise<Application[]>;
  moveStatus(id: number, status: Status): Promise<Application>;
}
