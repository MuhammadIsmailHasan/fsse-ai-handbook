// Server-only values: never import this module from a Client Component
// (in a real app, add `import "server-only"` at the top to make that a build error).
export type ServerEnv = { apiUrl: string; apiToken: string; appEnv: "development" | "test" | "production" };

const APP_ENVS = ["development", "test", "production"] as const;

export function readServerEnv(env: Record<string, string | undefined> = process.env): ServerEnv {
  const problems: string[] = [];

  const apiUrl = (env.API_URL ?? "").trim().replace(/\/+$/, "");
  if (!/^https?:\/\/[^\s/]+/.test(apiUrl)) problems.push("API_URL must be an http(s) URL");

  const apiToken = env.API_TOKEN ?? "";
  if (apiToken.length < 20) problems.push("API_TOKEN must be at least 20 characters");

  const appEnv = env.APP_ENV ?? "development";
  if (!(APP_ENVS as readonly string[]).includes(appEnv)) problems.push("APP_ENV must be development, test or production");

  if (problems.length > 0) throw new Error(`Invalid environment:\n- ${problems.join("\n- ")}`);
  return { apiUrl, apiToken, appEnv: appEnv as ServerEnv["appEnv"] };
}

// Browser-safe values. Literal references are inlined at build time; dynamic lookups are not.
export const publicEnv = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5091",
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "CareerPilot",
};
