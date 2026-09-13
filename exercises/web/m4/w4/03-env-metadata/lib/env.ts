// Environment variables. See README.md.
export type ServerEnv = { apiUrl: string; apiToken: string; appEnv: "development" | "test" | "production" };

export function readServerEnv(env: Record<string, string | undefined> = process.env): ServerEnv {
  throw new Error("TODO");
}

export const publicEnv = { apiUrl: "", appName: "" };
