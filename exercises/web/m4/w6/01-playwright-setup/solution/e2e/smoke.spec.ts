import { expect, test } from "@playwright/test";

test("logged-out visitors see the login page", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  await expect(page).toHaveTitle("Log in · CareerPilot");
});

test("a user can log in", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill("sari@example.com");
  await page.getByLabel("Password").fill("correct-horse");
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page.getByRole("heading", { name: "Applications" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Log out" })).toBeVisible();
});
