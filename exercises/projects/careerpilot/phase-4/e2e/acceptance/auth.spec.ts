import { expect, test } from "@playwright/test";
import { createUser, logIn, logInAndWait } from "./helpers";

test.describe("registration", () => {
  test("creates an account and opens the dashboard", async ({ page }) => {
    const email = `new.${Date.now()}.${Math.random().toString(36).slice(2)}@example.com`;
    await page.goto("/register");
    await page.getByLabel("Name").fill("Budi Santoso");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Password").fill("correct-horse-battery");
    await page.getByRole("button", { name: "Create account" }).click();
    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByRole("heading", { level: 1, name: "Dashboard" })).toBeVisible();
    await expect(page.getByText("Welcome, Budi Santoso")).toBeVisible();
  });

  test("rejects an email that is already registered", async ({ page, request }) => {
    const existing = await createUser(request);
    await page.goto("/register");
    await page.getByLabel("Name").fill("Someone Else");
    await page.getByLabel("Email").fill(existing.email.toUpperCase());
    await page.getByLabel("Password").fill("another-password");
    await page.getByRole("button", { name: "Create account" }).click();
    await expect(page.getByRole("alert").filter({ hasText: "An account with this email already exists" })).toBeVisible(); // (Next.js also renders an empty role="alert" route announcer)
    await expect(page).toHaveURL(/\/register/);
  });

  test("shows field errors from validation", async ({ page }) => {
    await page.goto("/register");
    await page.getByLabel("Name").fill("Budi");
    await page.getByLabel("Email").fill("budi@example.com");
    await page.getByLabel("Password").fill("short");
    await page.getByRole("button", { name: "Create account" }).click();
    await expect(page.getByLabel("Password")).toHaveAttribute("aria-invalid", "true");
    await expect(page).toHaveURL(/\/register/);
  });
});

test.describe("login and sessions", () => {
  test("wrong password shows a generic error", async ({ page, request }) => {
    const user = await createUser(request);
    await logIn(page, { ...user, password: "wrong-password" });
    await expect(page.getByRole("alert").filter({ hasText: "Invalid email or password" })).toBeVisible(); // (Next.js also renders an empty role="alert" route announcer)
    await expect(page).toHaveURL(/\/login/);
  });

  test("protected pages redirect to login and come back afterwards", async ({ page, request }) => {
    const user = await createUser(request);
    for (const path of ["/dashboard", "/applications", "/applications/new", "/companies"]) {
      await page.goto(path);
      await expect(page, path).toHaveURL(/\/login\?next=/);
    }
    await logIn(page, user, "/login?next=%2Fcompanies");
    await expect(page).toHaveURL(/\/companies$/);
  });

  test("the API token is never readable by JavaScript", async ({ page, context, request }) => {
    const user = await createUser(request);
    await logInAndWait(page, user);
    const exposed = await page.evaluate(() => [document.cookie, JSON.stringify({ ...localStorage }), JSON.stringify({ ...sessionStorage })].join(" "));
    expect(exposed).not.toContain("cpt_");
    const cookies = await context.cookies();
    expect(cookies.some((cookie) => cookie.httpOnly && cookie.sameSite !== "None")).toBe(true);
    expect(cookies.some((cookie) => cookie.value.includes("cpt_"))).toBe(false);
  });

  test("logged-in users skip the login page; logging out ends the session", async ({ page, request }) => {
    const user = await createUser(request);
    await logInAndWait(page, user);
    await page.goto("/login");
    await expect(page).toHaveURL(/\/dashboard$/);
    await page.getByRole("button", { name: "Log out" }).click();
    await expect(page).toHaveURL(/\/login/);
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login\?next=/);
  });
});
