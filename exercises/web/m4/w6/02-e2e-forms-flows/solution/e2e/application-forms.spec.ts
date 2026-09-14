import { expect, test, type Page } from "@playwright/test";
import { LoginPage, USER } from "./pages/login-page";
import { NewApplicationPage } from "./pages/new-application-page";

async function logIn(page: Page) {
  const login = new LoginPage(page);
  await login.goto();
  await login.login();
  await expect(page).toHaveURL(/\/applications$/);
}

test.describe("login", () => {
  test("wrong password shows a generic error and stays on the login page", async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.login(USER.email, "wrong-password");
    await expect(login.alert).toHaveText("Invalid email or password");
    await expect(page).toHaveURL(/\/login/);
  });

  test("returns to the page you wanted after logging in", async ({ page }) => {
    await page.goto("/applications/new");
    await expect(page).toHaveURL(/\/login\?next=/);
    await new LoginPage(page).login();
    await expect(page).toHaveURL(/\/applications\/new$/);
    await expect(page.getByRole("heading", { name: "New application" })).toBeVisible();
  });
});

test.describe("new application form", () => {
  test.beforeEach(async ({ page }) => logIn(page));

  test("role is required and typed values are kept", async ({ page }) => {
    const form = new NewApplicationPage(page);
    await form.goto();
    await form.fill({ company: "Kopi Data", salaryMin: "9000000" });
    await form.submit();
    await expect(page.getByText("Role is required")).toBeVisible();
    await expect(form.role).toHaveAttribute("aria-invalid", "true");
    await expect(form.salaryMin).toHaveValue("9000000");
    await expect(form.company).toHaveValue("1");
  });

  test("maximum salary must be at least the minimum", async ({ page }) => {
    const form = new NewApplicationPage(page);
    await form.goto();
    await form.fill({ company: "Kopi Data", role: "AI Engineer", salaryMin: "20000000", salaryMax: "10000000" });
    await form.submit();
    await expect(page.getByText("Maximum must be at least the minimum")).toBeVisible();
    await expect(form.salaryMax).toHaveAttribute("aria-invalid", "true");
  });

  test("a valid application is created and listed", async ({ page }) => {
    const form = new NewApplicationPage(page);
    await form.goto();
    await form.fill({ company: "Batik Cloud", role: "Platform Engineer", salaryMin: "15000000", salaryMax: "22000000" });
    await form.submit();
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Platform Engineer");
    await expect(page.getByRole("status")).toHaveText("Application created");

    await page.goto("/applications");
    await expect(page.getByRole("link", { name: "Platform Engineer" })).toBeVisible();
  });
});

test.describe("application page", () => {
  test.beforeEach(async ({ page }) => logIn(page));

  test("status changes are saved", async ({ page }) => {
    await page.getByRole("link", { name: "Backend Engineer" }).click();
    await page.getByLabel("Move to").selectOption("offer");
    await page.getByRole("button", { name: "Update status" }).click();
    await page.reload();
    await expect(page.getByTestId("status")).toHaveText("offer");
  });

  test("delete asks for confirmation", async ({ page }) => {
    await page.getByRole("link", { name: "Data Engineer" }).click();
    await page.getByRole("button", { name: "Delete" }).click();
    const dialog = page.getByRole("dialog", { name: 'Delete "Data Engineer"?' });
    await expect(dialog).toBeVisible();

    await dialog.getByRole("button", { name: "Cancel" }).click();
    await expect(dialog).toBeHidden();
    await page.goto("/applications");
    await expect(page.getByRole("link", { name: "Data Engineer" })).toBeVisible();

    await page.getByRole("link", { name: "Data Engineer" }).click();
    await page.getByRole("button", { name: "Delete" }).click();
    await page.getByRole("dialog").getByRole("button", { name: "Delete application" }).click();
    await expect(page.getByRole("status")).toHaveText("Application deleted");
    await expect(page.getByRole("link", { name: "Data Engineer" })).toHaveCount(0);
  });
});
