import "server-only";
// Data Access Layer. See README.md.

export async function verifySession(): Promise<{ userId: number; role: "member" | "admin"; accessToken: string }> {
  throw new Error("TODO");
}

export async function getCurrentUser(): Promise<{ id: number; role: "member" | "admin" }> {
  throw new Error("TODO");
}
