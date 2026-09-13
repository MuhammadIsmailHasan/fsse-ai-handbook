// Controlled inputs. See README.md.
import { useRef, useState, type FormEvent } from "react";

export type Company = { id: number; name: string };
export type ApplicationPayload = { companyId: number; role: string; salaryMin: number | null; salaryMax: number | null; remote: boolean; notes: string };

export function ApplicationForm(props: { onSubmit: (payload: ApplicationPayload) => void; companies: Company[] }) {
  return null;
}

export function SearchBox(props: { value: string; onChange: (value: string) => void }) {
  return null;
}
