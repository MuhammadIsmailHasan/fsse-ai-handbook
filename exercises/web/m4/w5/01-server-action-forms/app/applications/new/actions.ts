// Server Action. See README.md.
export type FormState = { message: string | null; fieldErrors: Partial<Record<"company_id" | "role" | "salary_min" | "salary_max", string[]>> };

export async function createApplicationAction(previousState: FormState, formData: FormData): Promise<FormState> {
  throw new Error("TODO");
}
