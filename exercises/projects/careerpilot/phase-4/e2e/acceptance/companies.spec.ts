import { expect, test as base, type Page } from "@playwright/test";
import { createApplication, createCompany, createUser, logInAndWait, type TestUser } from "./helpers";

// Every test gets a fresh, logged-in user on the Companies page.
const test = base.extend<{ user: TestUser }>({
  user: async ({ page, request }, use) => {
    const user = await createUser(request);
    await logInAndWait(page, user);
    await page.goto("/companies");
    await use(user);
  },
});

const companyList = (page: Page) => page.getByRole("list", { name: "Companies" });

test("adds companies and lists them by name", async ({ page, user }) => {
  void user;
  await expect(page.getByRole("heading", { level: 1, name: "Companies" })).toBeVisible();
  for (const name of ["zeta Labs", "Alpha Pay"]) {
    await page.getByLabel("Company name").fill(name);
    await page.getByRole("button", { name: "Add company" }).click();
    await expect(companyList(page).getByText(name)).toBeVisible();
  }
  await expect(companyList(page).getByRole("listitem")).toHaveText([/Alpha Pay/, /zeta Labs/]);
  await expect(page.getByLabel("Company name")).toHaveValue("");
});

test("rejects duplicates and invalid websites", async ({ page, user }) => {
  void user;
  await page.getByLabel("Company name").fill("Kopi Data");
  await page.getByRole("button", { name: "Add company" }).click();
  await expect(companyList(page).getByText("Kopi Data")).toBeVisible();

  await page.getByLabel("Company name").fill("kopi data");
  await page.getByRole("button", { name: "Add company" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "You already have a company with this name" })).toBeVisible(); // (Next.js also renders an empty role="alert" route announcer)

  await page.getByLabel("Company name").fill("Nusantara Pay");
  await page.getByLabel("Website").fill("nusantara.example");
  await page.getByRole("button", { name: "Add company" }).click();
  await expect(page.getByLabel("Website")).toHaveAttribute("aria-invalid", "true");
  await expect(companyList(page).getByText("Nusantara Pay")).toHaveCount(0);
});

test("deletes unused companies but not companies with applications", async ({ page, request, user }) => {
  const used = await createCompany(request, user, "Used Corp");
  await createCompany(request, user, "Unused Corp");
  await createApplication(request, user, { company_id: used.id, role: "Dev" });
  await page.reload();

  await page.getByRole("button", { name: "Delete Unused Corp" }).click();
  await expect(companyList(page).getByText("Unused Corp")).toHaveCount(0);

  await page.getByRole("button", { name: "Delete Used Corp" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "This company still has applications" })).toBeVisible(); // (Next.js also renders an empty role="alert" route announcer)
  await expect(companyList(page).getByText("Used Corp")).toBeVisible();
});
