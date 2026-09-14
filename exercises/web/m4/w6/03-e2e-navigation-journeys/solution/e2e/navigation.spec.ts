import { expect, test } from "@playwright/test";

test.describe("without a session", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("protected pages redirect to login", async ({ page }) => {
    await page.goto("/applications");
    await expect(page).toHaveURL(/\/login\?next=%2Fapplications/);
    await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  });
});

test("the active link is marked for assistive technology", async ({ page }) => {
  await page.goto("/jobs");
  const nav = page.getByRole("navigation", { name: "Main" });
  await expect(nav.getByRole("link", { name: "Jobs" })).toHaveAttribute("aria-current", "page");
  await expect(nav.getByRole("link", { name: "Applications" })).not.toHaveAttribute("aria-current");
});

test("search lives in the URL and survives a reload", async ({ page }) => {
  await page.goto("/jobs");
  await page.getByLabel("Search jobs").fill("data");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page).toHaveURL(/[?&]q=data/);
  await expect(page.getByTestId("result-count")).toHaveText("5 jobs found");
  await page.reload();
  await expect(page.getByTestId("result-count")).toHaveText("5 jobs found");
  await expect(page.getByLabel("Search jobs")).toHaveValue("data");
});

test("pagination and the back button", async ({ page }) => {
  await page.goto("/jobs");
  const pagination = page.getByRole("navigation", { name: "Pagination" });
  await expect(pagination).toContainText("Page 1 of 3");
  await pagination.getByRole("link", { name: "Next page" }).click();
  await expect(page).toHaveURL(/page=2/);
  await expect(pagination).toContainText("Page 2 of 3");
  await page.goBack();
  await expect(pagination).toContainText("Page 1 of 3");
});

test("unknown applications return a real 404", async ({ page }) => {
  const response = await page.goto("/applications/9999");
  expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { name: "Application not found" })).toBeVisible();
});

test("application pages have a descriptive title and breadcrumb", async ({ page }) => {
  await page.goto("/applications");
  await page.getByRole("link", { name: "Data Engineer" }).click();
  await expect(page).toHaveTitle("Data Engineer · CareerPilot");
  await page.getByRole("navigation", { name: "Breadcrumb" }).getByRole("link", { name: "Applications" }).click();
  await expect(page).toHaveURL(/\/applications$/);
});
