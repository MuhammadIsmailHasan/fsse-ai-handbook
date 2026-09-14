import { expect, test } from "@playwright/test";
import { createApplication, createCompany, createUser, logInAndWait, moveStatus } from "./helpers";

test("dashboard shows stats from the API", async ({ page, request }) => {
  const user = await createUser(request);
  const company = await createCompany(request, user, "Kopi Data");
  const a = await createApplication(request, user, { company_id: company.id, role: "Backend Engineer" });
  const b = await createApplication(request, user, { company_id: company.id, role: "Data Engineer" });
  await createApplication(request, user, { company_id: company.id, role: "AI Engineer" });
  await moveStatus(request, user, a.id, "applied", "interview");
  await moveStatus(request, user, b.id, "rejected");

  await logInAndWait(page, user);
  await expect(page.getByTestId("stat-total")).toHaveText("3");
  await expect(page.getByTestId("stat-active")).toHaveText("2");
  await expect(page.getByTestId("stat-interview")).toHaveText("1");
  await expect(page.getByTestId("stat-rejected")).toHaveText("1");
  await expect(page.getByTestId("stat-offer")).toHaveText("0");
});

test("main navigation marks the current page", async ({ page, request }) => {
  const user = await createUser(request);
  await logInAndWait(page, user);
  const nav = page.getByRole("navigation", { name: "Main" });
  await expect(nav.getByRole("link", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
  await nav.getByRole("link", { name: "Companies" }).click();
  await expect(page).toHaveURL(/\/companies$/);
  await expect(nav.getByRole("link", { name: "Companies" })).toHaveAttribute("aria-current", "page");
  await expect(nav.getByRole("link", { name: "Dashboard" })).not.toHaveAttribute("aria-current");
  await nav.getByRole("link", { name: "Applications" }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Applications" })).toBeVisible();
});

test("pages have descriptive titles", async ({ page, request }) => {
  const user = await createUser(request);
  const company = await createCompany(request, user, "Batik Cloud");
  const app = await createApplication(request, user, { company_id: company.id, role: "Platform Engineer" });
  await logInAndWait(page, user);
  await expect(page).toHaveTitle("Dashboard · CareerPilot");
  await page.goto(`/applications/${app.id}`);
  await expect(page).toHaveTitle("Platform Engineer at Batik Cloud · CareerPilot");
});

test("unknown and other users' applications are real 404s", async ({ page, request }) => {
  const owner = await createUser(request, "Owner");
  const company = await createCompany(request, owner, "Secret Corp");
  const secret = await createApplication(request, owner, { company_id: company.id, role: "Secret Role" });

  const user = await createUser(request);
  await logInAndWait(page, user);
  for (const path of ["/applications/999999", `/applications/${secret.id}`]) {
    const response = await page.goto(path);
    expect(response?.status(), path).toBe(404);
    await expect(page.getByRole("heading", { name: "Application not found" })).toBeVisible();
    await expect(page.getByText("Secret Role")).toHaveCount(0);
  }
});
