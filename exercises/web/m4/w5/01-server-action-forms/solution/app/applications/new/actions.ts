"use server";

import { updateTag } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { ApiError, createApplication } from "../../../lib/api";
import { applicationSchema } from "./schema";

export type FormState = { message: string | null; fieldErrors: Partial<Record<"company_id" | "role" | "salary_min" | "salary_max", string[]>> };

export async function createApplicationAction(_previousState: FormState, formData: FormData): Promise<FormState> {
  // (In the real app: verify the session here first — actions are public POST endpoints.)
  const parsed = applicationSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return { message: "Please fix the errors below", fieldErrors: z.flattenError(parsed.error).fieldErrors };
  }

  let created: { id: number };
  try {
    created = await createApplication(parsed.data);
  } catch (error) {
    if (error instanceof ApiError && error.status === 422) return { message: "Please fix the errors below", fieldErrors: error.fields ?? {} };
    if (error instanceof ApiError && error.status === 409) return { message: "You already have an application for this role", fieldErrors: {} };
    throw error; // unexpected → error boundary
  }

  updateTag("applications");
  redirect(`/applications/${created.id}`); // outside try/catch: redirect works by throwing
}
