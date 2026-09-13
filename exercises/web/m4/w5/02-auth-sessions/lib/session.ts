import "server-only";
// Encrypted session cookie. See README.md.

export type SessionPayload = { userId: number; role: "member" | "admin"; accessToken: string; expiresAt: string };

export async function encrypt(payload: SessionPayload): Promise<string> {
  throw new Error("TODO");
}

export async function decrypt(token: string | undefined): Promise<SessionPayload | null> {
  throw new Error("TODO");
}

export async function createSession(user: { id: number; role: "member" | "admin" }, accessToken: string): Promise<void> {
  throw new Error("TODO");
}

export async function deleteSession(): Promise<void> {
  throw new Error("TODO");
}
