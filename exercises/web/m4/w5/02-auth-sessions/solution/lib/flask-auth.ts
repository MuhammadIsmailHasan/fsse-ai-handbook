// Provided: talks to the Flask API (server-side only).
export class InvalidCredentials extends Error {}

export type FlaskUser = { id: number; name: string; role: "member" | "admin" };

export async function loginWithFlask(email: string, password: string): Promise<{ accessToken: string; user: FlaskUser }> {
  const response = await fetch(`${process.env.API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (response.status === 401) throw new InvalidCredentials();
  if (!response.ok) throw new Error(`Login failed with ${response.status}`);
  const body = await response.json();
  return { accessToken: body.data.access_token, user: body.data.user };
}
