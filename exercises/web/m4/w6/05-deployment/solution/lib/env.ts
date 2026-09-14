import { z } from "zod";

const serverEnvSchema = z.object({
  API_URL: z.url(),
  SESSION_SECRET: z.string().min(32),
  NEXT_PUBLIC_APP_URL: z.url(),
});

export type ServerEnv = z.infer<typeof serverEnvSchema>;

export function parseServerEnv(source: Record<string, string | undefined> = process.env): ServerEnv {
  const result = serverEnvSchema.safeParse(source);
  if (!result.success) {
    // Names only: error messages end up in logs, and logs must never contain secrets.
    const names = [...new Set(result.error.issues.map((issue) => String(issue.path[0])))].sort();
    throw new Error(`Invalid environment variables: ${names.join(", ")}`);
  }
  return result.data;
}
