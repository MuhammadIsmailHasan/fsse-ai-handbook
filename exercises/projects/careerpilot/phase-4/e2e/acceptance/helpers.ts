// Shared helpers for the acceptance tests. Don't change them — they define the contract.
import { expect, type APIRequestContext, type Page } from "@playwright/test";
import { randomUUID } from "node:crypto";

export const API = `http://localhost:${process.env.MOCK_API_PORT ?? 5093}/api/v1`;

export const STATUS_LABELS = {
  saved: "Saved",
  applied: "Applied",
  screening: "Screening",
  interview: "Interview",
  offer: "Offer",
  accepted: "Accepted",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
} as const;

export type TestUser = { name: string; email: string; password: string; token: string };

/** Registers a brand-new user through the API (so every test has its own data) and returns its token. */
export async function createUser(request: APIRequestContext, name = "Sari Wulandari"): Promise<TestUser> {
  const user = { name, email: `sari.${randomUUID()}@example.com`, password: "correct-horse-battery" };
  expect((await request.post(`${API}/auth/register`, { data: user })).status()).toBe(201);
  const login = await request.post(`${API}/auth/login`, { data: { email: user.email, password: user.password } });
  const token = (await login.json()).data.access_token as string;
  return { ...user, token };
}

const auth = (user: TestUser) => ({ Authorization: `Bearer ${user.token}` });

export async function createCompany(request: APIRequestContext, user: TestUser, name: string): Promise<{ id: number; name: string }> {
  const response = await request.post(`${API}/companies`, { data: { name }, headers: auth(user) });
  expect(response.status()).toBe(201);
  return (await response.json()).data;
}

export async function createApplication(
  request: APIRequestContext,
  user: TestUser,
  data: { company_id: number; role: string; salary_min?: number; salary_max?: number },
): Promise<{ id: number; role: string }> {
  const response = await request.post(`${API}/applications`, { data, headers: auth(user) });
  expect(response.status()).toBe(201);
  return (await response.json()).data;
}

export async function moveStatus(request: APIRequestContext, user: TestUser, applicationId: number, ...statuses: string[]) {
  for (const status of statuses) {
    const response = await request.post(`${API}/applications/${applicationId}/status`, { data: { status }, headers: auth(user) });
    expect(response.status()).toBe(200);
  }
}

/** Logs in through YOUR login page. */
export async function logIn(page: Page, user: TestUser, path = "/login") {
  await page.goto(path);
  await page.getByLabel("Email").fill(user.email);
  await page.getByLabel("Password").fill(user.password);
  await page.getByRole("button", { name: "Log in" }).click();
}

export async function logInAndWait(page: Page, user: TestUser) {
  await logIn(page, user);
  await expect(page).toHaveURL(/\/dashboard$/);
}
