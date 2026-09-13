// Browser-side client for our BFF. See README.md.
export class ApiError extends Error {
  constructor(public status: number, public code: string) {
    super(code);
  }
}

export type Application = { id: number; role: string; status: string };

export const applicationsClient = {
  async list(status?: string): Promise<Application[]> {
    throw new Error("TODO");
  },
  async create(input: { company_id: number; role: string }): Promise<Application> {
    throw new Error("TODO");
  },
  async update(id: number, patch: Partial<Pick<Application, "role" | "status">>): Promise<Application> {
    throw new Error("TODO");
  },
  async remove(id: number): Promise<null> {
    throw new Error("TODO");
  },
};
