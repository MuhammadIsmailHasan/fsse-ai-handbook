"use client";
// RHF + Zod form. See README.md.
import type { ProfileValues } from "./profile-schema";

export type ServerResult = void | { fieldErrors?: Partial<Record<"name" | "email" | "headline", string>>; message?: string };

export function ProfileForm(props: { defaultValues: ProfileValues; onSubmit: (values: ProfileValues) => Promise<ServerResult> }) {
  return null;
}
