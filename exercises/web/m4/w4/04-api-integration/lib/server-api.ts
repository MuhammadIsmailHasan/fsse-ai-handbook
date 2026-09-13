// Provided: builds the API client for Server Components (reads the session cookie and server-only env).
import { cookies } from "next/headers";
import { createApiClient } from "./api-client";

export async function getServerApi() {
  const token = (await cookies()).get("session")?.value;
  return createApiClient({ baseUrl: process.env.API_URL ?? "http://localhost:5091", getToken: () => token });
}
