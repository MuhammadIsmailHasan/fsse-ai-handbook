// @vitest-environment node
import { readFileSync } from "node:fs";
import { SignJWT } from "jose";
import { NextRequest } from "next/server";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const mocks = vi.hoisted(() => {
  const jar = new Map<string, { value: string; options?: Record<string, unknown> }>();
  return {
    jar,
    cookieStore: {
      get: vi.fn((name: string) => (jar.has(name) ? { name, value: jar.get(name)!.value } : undefined)),
      set: vi.fn((name: string, value: string, options?: Record<string, unknown>) => void jar.set(name, { value, options })),
      delete: vi.fn((name: string) => void jar.delete(name)),
    },
    redirect: vi.fn((url: string) => {
      throw Object.assign(new Error("NEXT_REDIRECT"), { url });
    }),
    loginWithFlask: vi.fn(),
  };
});
vi.mock("server-only", () => ({}));
vi.mock("next/headers", () => ({ cookies: async () => mocks.cookieStore }));
vi.mock("next/navigation", () => ({ redirect: mocks.redirect }));
vi.mock("./lib/flask-auth", async (importOriginal) => ({ ...(await importOriginal<typeof import("./lib/flask-auth")>()), loginWithFlask: mocks.loginWithFlask }));

import { login, logout } from "./app/login/actions";
import { getCurrentUser, verifySession } from "./lib/dal";
import { InvalidCredentials } from "./lib/flask-auth";
import { safeNextPath } from "./lib/safe-redirect";
import { createSession, decrypt, deleteSession, encrypt, type SessionPayload } from "./lib/session";
import proxy, { config } from "./proxy";

const SECRET = "test-secret-that-is-long-enough-1234567890";
const payload: SessionPayload = { userId: 7, role: "member", accessToken: "flask-token-abc", expiresAt: "2030-01-01T00:00:00.000Z" };
const form = (values: Record<string, string>) => {
  const data = new FormData();
  Object.entries(values).forEach(([k, v]) => data.append(k, v));
  return data;
};
const read = (file: string) => readFileSync(`${import.meta.dirname}/${file}`, "utf8");

beforeEach(() => {
  vi.stubEnv("SESSION_SECRET", SECRET);
  mocks.jar.clear();
  mocks.redirect.mockClear();
  mocks.loginWithFlask.mockReset();
  mocks.cookieStore.set.mockClear();
});
afterEach(() => {
  vi.unstubAllEnvs();
  vi.useRealTimers();
});

describe("session tokens", () => {
  test("round trip with HS256 and a 7 day expiry", async () => {
    const token = await encrypt(payload);
    expect(JSON.parse(Buffer.from(token.split(".")[0]!, "base64url").toString())).toEqual({ alg: "HS256" });
    const decoded = await decrypt(token);
    expect(decoded).toMatchObject(payload);
    const claims = decoded as unknown as { iat: number; exp: number };
    expect(claims.exp - claims.iat).toBe(7 * 24 * 60 * 60);
  });

  test("rejects missing, tampered, wrongly-signed and expired tokens", async () => {
    expect(await decrypt(undefined)).toBeNull();
    expect(await decrypt("not-a-jwt")).toBeNull();
    const token = await encrypt(payload);
    const [h, , s] = token.split(".");
    const forged = Buffer.from(JSON.stringify({ ...payload, role: "admin" })).toString("base64url");
    expect(await decrypt(`${h}.${forged}.${s}`)).toBeNull();
    const otherKey = await new SignJWT(payload).setProtectedHeader({ alg: "HS256" }).setExpirationTime("7d").sign(new TextEncoder().encode("another-secret-another-secret-another"));
    expect(await decrypt(otherKey)).toBeNull();
    const expired = await new SignJWT(payload).setProtectedHeader({ alg: "HS256" }).setExpirationTime(Math.floor(Date.now() / 1000) - 60).sign(new TextEncoder().encode(SECRET));
    expect(await decrypt(expired)).toBeNull();
  });

  test("cookie flags", async () => {
    const now = Math.floor(Date.now() / 1000) * 1000;
    vi.useFakeTimers({ now });
    await createSession({ id: 7, role: "member" }, "flask-token-abc");
    const cookie = mocks.jar.get("session")!;
    expect(cookie.options).toMatchObject({ httpOnly: true, secure: true, sameSite: "lax", path: "/" });
    expect((cookie.options!.expires as Date).getTime()).toBe(now + 7 * 24 * 60 * 60 * 1000);
    vi.useRealTimers();
    expect(await decrypt(cookie.value)).toMatchObject({ userId: 7, role: "member", accessToken: "flask-token-abc" });
    await deleteSession();
    expect(mocks.jar.has("session")).toBe(false);
  });

  test("server-only modules", () => {
    expect(read("lib/session.ts")).toMatch(/^import ["']server-only["']/m);
    expect(read("lib/dal.ts")).toMatch(/^import ["']server-only["']/m);
  });
});

test("safeNextPath blocks open redirects", () => {
  expect(safeNextPath("/applications/3?tab=notes")).toBe("/applications/3?tab=notes");
  for (const bad of ["https://evil.example", "//evil.example", "/\\evil.example", "javascript:alert(1)", "", null, 42, "dashboard"]) {
    expect(safeNextPath(bad)).toBe("/dashboard");
  }
});

describe("login and logout actions", () => {
  test("validation and invalid credentials share generic messages", async () => {
    expect(read("app/login/actions.ts").trimStart()).toMatch(/^["']use server["']/);
    await expect(login({ message: null }, form({ email: "nope", password: "" }))).resolves.toEqual({ message: "Enter your email and password" });
    expect(mocks.loginWithFlask).not.toHaveBeenCalled();
    mocks.loginWithFlask.mockRejectedValueOnce(new InvalidCredentials());
    await expect(login({ message: null }, form({ email: "sari@example.com", password: "wrong" }))).resolves.toEqual({ message: "Invalid email or password" });
    expect(mocks.jar.has("session")).toBe(false);
    mocks.loginWithFlask.mockRejectedValueOnce(new Error("Login failed with 500"));
    await expect(login({ message: null }, form({ email: "sari@example.com", password: "x" }))).rejects.toThrow("500");
  });

  test("success creates the session and redirects safely", async () => {
    mocks.loginWithFlask.mockResolvedValue({ accessToken: "tok-1", user: { id: 7, name: "Sari", role: "member" } });
    await expect(login({ message: null }, form({ email: "sari@example.com", password: "pw", next: "/applications/9" }))).rejects.toMatchObject({ url: "/applications/9" });
    expect(mocks.loginWithFlask).toHaveBeenCalledWith("sari@example.com", "pw");
    expect(await decrypt(mocks.jar.get("session")!.value)).toMatchObject({ userId: 7, accessToken: "tok-1" });
    await expect(login({ message: null }, form({ email: "sari@example.com", password: "pw", next: "https://evil.example" }))).rejects.toMatchObject({ url: "/dashboard" });
  });

  test("logout", async () => {
    mocks.jar.set("session", { value: await encrypt(payload) });
    await expect(logout()).rejects.toMatchObject({ url: "/login" });
    expect(mocks.jar.has("session")).toBe(false);
  });
});

describe("data access layer", () => {
  test("redirects without a valid session", async () => {
    await expect(verifySession()).rejects.toMatchObject({ url: "/login" });
    mocks.jar.set("session", { value: "garbage" });
    await expect(verifySession()).rejects.toMatchObject({ url: "/login" });
  });

  test("returns session, and a DTO without the token", async () => {
    mocks.jar.set("session", { value: await encrypt(payload) });
    await expect(verifySession()).resolves.toEqual({ userId: 7, role: "member", accessToken: "flask-token-abc" });
    await expect(getCurrentUser()).resolves.toEqual({ id: 7, role: "member" });
    expect(read("lib/dal.ts")).toMatch(/cache\(/);
  });
});

describe("proxy", () => {
  const request = async (path: string, withSession = false) => {
    const req = new NextRequest(`http://localhost:3091${path}`);
    if (withSession) req.cookies.set("session", await encrypt(payload));
    return proxy(req);
  };

  test("redirects anonymous users from protected pages, keeping where they were going", async () => {
    const response = await request("/applications/3?tab=notes");
    expect(response.status).toBe(307);
    const location = new URL(response.headers.get("location")!);
    expect(location.pathname).toBe("/login");
    expect(location.searchParams.get("next")).toBe("/applications/3?tab=notes");
    expect((await request("/dashboard")).headers.get("location")).toContain("/login");
  });

  test("lets requests through otherwise", async () => {
    for (const [path, session] of [["/", false], ["/jobs", false], ["/dashboards-public", false], ["/dashboard", true], ["/applications", true]] as const) {
      const response = await request(path, session);
      expect(response.headers.get("location"), path).toBeNull();
      expect(response.headers.get("x-middleware-next"), path).toBe("1");
    }
  });

  test("sends logged-in users away from /login", async () => {
    expect(new URL((await request("/login", true)).headers.get("location")!).pathname).toBe("/dashboard");
    expect((await request("/login")).headers.get("location")).toBeNull();
  });

  test("matcher skips static assets and api", () => {
    const pattern = new RegExp(`^${config.matcher[0]!.replace("/((?!", "/(?!(?:").replace(").*)", ")).*")}$`);
    expect(pattern.test("/dashboard")).toBe(true);
    for (const skipped of ["/api/applications", "/_next/static/chunk.js", "/_next/image", "/favicon.ico"]) expect(pattern.test(skipped), skipped).toBe(false);
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});
