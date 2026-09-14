import { expect, test } from "@playwright/test";

test.describe("logging out", () => {
  // Fresh login: logging out the shared session would break every other test.
  test.use({ storageState: { cookies: [], origins: [] } });

  test("ends the session", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill("sari@example.com");
    await page.getByLabel("Password").fill("correct-horse");
    await page.getByRole("button", { name: "Log in" }).click();
    await page.getByRole("button", { name: "Log out" }).click();
    await expect(page).toHaveURL(/\/login/);
    await page.goto("/applications");
    await expect(page).toHaveURL(/\/login\?next=/);
  });
});

test.describe("job seeker journey", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("moves an application forward", async ({ page }) => {
    await test.step("log in and open the dashboard", async () => {
      await page.goto("/login");
      await page.getByLabel("Email").fill("sari@example.com");
      await page.getByLabel("Password").fill("correct-horse");
      await page.getByRole("button", { name: "Log in" }).click();
      await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Dashboard" }).click();
      await expect(page.getByRole("heading", { name: /Welcome back/ })).toBeVisible();
    });

    await test.step("open the application", async () => {
      await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Applications" }).click();
      await page.getByRole("link", { name: "Backend Engineer" }).click();
      await expect(page.getByRole("heading", { level: 1 })).toHaveText("Backend Engineer");
    });

    await test.step("move it to interview", async () => {
      await page.getByLabel("Move to").selectOption("interview");
      await page.getByRole("button", { name: "Update status" }).click();
      await expect(page.getByRole("status")).toHaveText("Status updated");
    });

    await test.step("see it in the list", async () => {
      await page.getByRole("navigation", { name: "Breadcrumb" }).getByRole("link", { name: "Applications" }).click();
      await expect(page.getByRole("row", { name: /Backend Engineer/ })).toContainText("interview");
    });
  });
});
