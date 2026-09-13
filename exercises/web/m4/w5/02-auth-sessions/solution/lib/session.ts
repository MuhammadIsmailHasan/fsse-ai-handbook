import "server-only";
import { jwtVerify, SignJWT } from "jose";
import { cookies } from "next/headers";

export type SessionPayload = { userId: number; role: "member" | "admin"; accessToken: string; expiresAt: string };

const SESSION_COOKIE = "session";
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

function secretKey() {
  const secret = process.env.SESSION_SECRET;
  if (!secret || secret.length < 32) throw new Error("SESSION_SECRET must be at least 32 characters");
  return new TextEncoder().encode(secret);
}

export async function encrypt(payload: SessionPayload): Promise<string> {
  return new SignJWT(payload).setProtectedHeader({ alg: "HS256" }).setIssuedAt().setExpirationTime("7d").sign(secretKey());
}

export async function decrypt(token: string | undefined): Promise<SessionPayload | null> {
  if (!token) return null;
  try {
    const { payload } = await jwtVerify<SessionPayload>(token, secretKey(), { algorithms: ["HS256"] });
    return payload;
  } catch {
    return null; // tampered, expired or malformed → treat as logged out
  }
}

export async function createSession(user: { id: number; role: "member" | "admin" }, accessToken: string): Promise<void> {
  const expires = new Date(Date.now() + SEVEN_DAYS_MS);
  const token = await encrypt({ userId: user.id, role: user.role, accessToken, expiresAt: expires.toISOString() });
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, token, { httpOnly: true, secure: true, sameSite: "lax", path: "/", expires });
}

export async function deleteSession(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(SESSION_COOKIE);
}
