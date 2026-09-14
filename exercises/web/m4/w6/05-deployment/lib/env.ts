// Environment validation. See README.md.
export type ServerEnv = { API_URL: string; SESSION_SECRET: string; NEXT_PUBLIC_APP_URL: string };

export function parseServerEnv(source: Record<string, string | undefined> = process.env): ServerEnv {
  throw new Error("TODO");
}
