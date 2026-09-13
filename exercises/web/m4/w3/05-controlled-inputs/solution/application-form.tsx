"use client";

import { useRef, useState, type FormEvent } from "react";

export type Company = { id: number; name: string };
export type ApplicationPayload = { companyId: number; role: string; salaryMin: number | null; salaryMax: number | null; remote: boolean; notes: string };

type Values = { companyId: string; role: string; salaryMin: string; salaryMax: string; remote: boolean; notes: string };
type Field = "company" | "role" | "salaryMax";
type Errors = Partial<Record<Field, string>>;

const EMPTY: Values = { companyId: "", role: "", salaryMin: "", salaryMax: "", remote: false, notes: "" };
const MAX_NOTES = 500;
const toNumber = (value: string) => (value.trim() === "" ? null : Number(value));

function validate(values: Values): Errors {
  const errors: Errors = {};
  if (values.companyId === "") errors.company = "Choose a company";
  if (values.role.trim() === "") errors.role = "Role is required";
  const min = toNumber(values.salaryMin);
  const max = toNumber(values.salaryMax);
  if (min !== null && max !== null && min > max) errors.salaryMax = "Maximum must be at least the minimum";
  return errors;
}

export function ApplicationForm({ onSubmit, companies }: { onSubmit: (payload: ApplicationPayload) => void; companies: Company[] }) {
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const refs = {
    company: useRef<HTMLSelectElement>(null),
    role: useRef<HTMLInputElement>(null),
    salaryMax: useRef<HTMLInputElement>(null),
  };

  // One generic setter for every field keeps handlers short.
  const set = <K extends keyof Values>(key: K, value: Values[K]) => setValues((previous) => ({ ...previous, [key]: value }));

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const found = validate(values);
    setErrors(found);
    const firstInvalid = (["company", "role", "salaryMax"] as const).find((field) => found[field]);
    if (firstInvalid) {
      refs[firstInvalid].current?.focus();
      return;
    }
    onSubmit({
      companyId: Number(values.companyId),
      role: values.role.trim(),
      salaryMin: toNumber(values.salaryMin),
      salaryMax: toNumber(values.salaryMax),
      remote: values.remote,
      notes: values.notes,
    });
    setValues(EMPTY);
  }

  const errorProps = (field: Field) =>
    errors[field] ? { "aria-invalid": true as const, "aria-describedby": `${field}-error` } : {};

  return (
    <form onSubmit={handleSubmit} noValidate>
      <label htmlFor="company">Company</label>
      <select id="company" ref={refs.company} value={values.companyId} onChange={(e) => set("companyId", e.target.value)} {...errorProps("company")}>
        <option value="">Choose a company</option>
        {companies.map((company) => (
          <option key={company.id} value={company.id}>
            {company.name}
          </option>
        ))}
      </select>
      {errors.company && <p id="company-error">{errors.company}</p>}

      <label htmlFor="role">Role</label>
      <input id="role" ref={refs.role} value={values.role} onChange={(e) => set("role", e.target.value)} {...errorProps("role")} />
      {errors.role && <p id="role-error">{errors.role}</p>}

      <label htmlFor="salaryMin">Minimum salary</label>
      <input id="salaryMin" type="number" min="0" value={values.salaryMin} onChange={(e) => set("salaryMin", e.target.value)} />

      <label htmlFor="salaryMax">Maximum salary</label>
      <input id="salaryMax" type="number" min="0" ref={refs.salaryMax} value={values.salaryMax} onChange={(e) => set("salaryMax", e.target.value)} {...errorProps("salaryMax")} />
      {errors.salaryMax && <p id="salaryMax-error">{errors.salaryMax}</p>}

      <label>
        <input type="checkbox" checked={values.remote} onChange={(e) => set("remote", e.target.checked)} /> Remote
      </label>

      <label htmlFor="notes">Notes</label>
      <textarea id="notes" maxLength={MAX_NOTES} value={values.notes} onChange={(e) => set("notes", e.target.value)} />
      <p>
        {values.notes.length}/{MAX_NOTES}
      </p>

      <button type="submit">Save application</button>
    </form>
  );
}

export function SearchBox({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  return (
    <div>
      <label htmlFor="application-search">Search applications</label>
      <input id="application-search" ref={inputRef} type="search" value={value} onChange={(e) => onChange(e.target.value)} />
      {value !== "" && (
        <button
          type="button"
          onClick={() => {
            onChange("");
            inputRef.current?.focus();
          }}
        >
          Clear
        </button>
      )}
    </div>
  );
}
