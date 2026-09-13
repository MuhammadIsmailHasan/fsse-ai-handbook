"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import { createApplicationAction, type FormState } from "./actions";

const initialState: FormState = { message: null, fieldErrors: {} };

function SubmitButton() {
  const { pending } = useFormStatus(); // reads the status of the parent <form>
  return (
    <button type="submit" disabled={pending}>
      {pending ? "Saving…" : "Save application"}
    </button>
  );
}

export function ApplicationForm({ companies }: { companies: { id: number; name: string }[] }) {
  const [state, formAction] = useActionState(createApplicationAction, initialState);

  const errorFor = (name: keyof FormState["fieldErrors"]) => state.fieldErrors[name]?.[0];
  const fieldProps = (name: keyof FormState["fieldErrors"]) => ({
    id: name,
    name,
    ...(errorFor(name) ? { "aria-invalid": true as const, "aria-describedby": `${name}-error` } : {}),
  });
  const error = (name: keyof FormState["fieldErrors"]) => errorFor(name) && <p id={`${name}-error`}>{errorFor(name)}</p>;

  return (
    <form action={formAction}>
      {state.message && <p role="alert">{state.message}</p>}

      <label htmlFor="company_id">Company</label>
      <select {...fieldProps("company_id")} defaultValue="">
        <option value="">Choose a company</option>
        {companies.map((company) => (
          <option key={company.id} value={company.id}>
            {company.name}
          </option>
        ))}
      </select>
      {error("company_id")}

      <label htmlFor="role">Role</label>
      <input {...fieldProps("role")} />
      {error("role")}

      <label htmlFor="salary_min">Minimum salary</label>
      <input {...fieldProps("salary_min")} type="number" min="0" />
      {error("salary_min")}

      <label htmlFor="salary_max">Maximum salary</label>
      <input {...fieldProps("salary_max")} type="number" min="0" />
      {error("salary_max")}

      <SubmitButton />
    </form>
  );
}
