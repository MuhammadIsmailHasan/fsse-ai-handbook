import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { cache } from "react";
import { decrypt } from "./session";

// cache() → one cookie decrypt per server render, however many components ask.
export const verifySession = cache(async () => {
  const token = (await cookies()).get("session")?.value;
  const session = await decrypt(token);
  if (!session?.userId) redirect("/login");
  return { userId: session.userId, role: session.role, accessToken: session.accessToken };
});

// DTO: only what the UI needs. The access token stays on the server.
export async function getCurrentUser(): Promise<{ id: number; role: "member" | "admin" }> {
  const session = await verifySession();
  return { id: session.userId, role: session.role };
}
