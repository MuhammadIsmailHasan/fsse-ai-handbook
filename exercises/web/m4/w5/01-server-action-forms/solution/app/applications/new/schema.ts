import { z } from "zod";

// FormData values are always strings: "" means "not provided".
const optionalSalary = z.preprocess(
  (value) => (value === "" || value === null || value === undefined ? undefined : value),
  z.coerce.number().int("Use a whole number").nonnegative("Salary can't be negative").optional(),
);

export const applicationSchema = z
  .object({
    company_id: z.coerce.number({ error: "Choose a company" }).int("Choose a company").positive("Choose a company"),
    role: z.string().trim().min(1, "Role is required").max(200, "Role is too long"),
    salary_min: optionalSalary,
    salary_max: optionalSalary,
  })
  .refine((data) => data.salary_min === undefined || data.salary_max === undefined || data.salary_min <= data.salary_max, {
    message: "Maximum must be at least the minimum",
    path: ["salary_max"],
  });

export type ApplicationInput = z.infer<typeof applicationSchema>;
