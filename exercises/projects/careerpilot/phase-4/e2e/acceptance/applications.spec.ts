import { expect, test, type Page } from "@playwright/test";
import { createApplication, createCompany, createUser, logInAndWait, moveStatus, STATUS_LABELS } from "./helpers";

const rows = (page: Page) => page.getByRole("table").getByRole("row").filter({ has: page.getByRole("cell") });

test.describe("list", () => {
  test("empty state and a hint to add a company first", async ({ page, request }) => {
    const user = await createUser(request);
    await logInAndWait(page, user);
    await page.goto("/applications");
    await expect(page.getByText("No applications yet")).toBeVisible();
    await page.getByRole("link", { name: "New application" }).click();
    await expect(page).toHaveURL(/\/applications\/new$/);
    await expect(page.getByText("Add a company first")).toBeVisible();
    await page.getByRole("main").getByRole("link", { name: "Companies" }).click();
    await expect(page).toHaveURL(/\/companies$/);
  });

  test("filters by status and search, kept in the URL", async ({ page, request }) => {
    const user = await createUser(request);
    const company = await createCompany(request, user, "Kopi Data");
    const a = await createApplication(request, user, { company_id: company.id, role: "Backend Engineer" });
    await createApplication(request, user, { company_id: company.id, role: "Data Engineer" });
    const c = await createApplication(request, user, { company_id: company.id, role: "Big Data Analyst" });
    await moveStatus(request, user, a.id, "applied");
    await moveStatus(request, user, c.id, "applied");

    await logInAndWait(page, user);
    await page.goto("/applications");
    await expect(rows(page)).toHaveCount(3);
    await expect(rows(page).first()).toContainText("Big Data Analyst");
    await expect(rows(page).filter({ hasText: "Backend Engineer" })).toContainText("Kopi Data");
    await expect(rows(page).filter({ hasText: "Backend Engineer" })).toContainText(STATUS_LABELS.applied);

    await page.getByLabel("Status").selectOption("applied");
    await page.getByRole("button", { name: "Apply filters" }).click();
    await expect(page).toHaveURL(/status=applied/);
    await expect(rows(page)).toHaveCount(2);

    await page.getByLabel("Search").fill("data");
    await page.getByRole("button", { name: "Apply filters" }).click();
    await expect(page).toHaveURL(/q=data/);
    await expect(rows(page)).toHaveCount(1);
    await expect(rows(page)).toContainText("Big Data Analyst");

    await page.reload();
    await expect(rows(page)).toHaveCount(1);
    await expect(page.getByLabel("Search")).toHaveValue("data");
    await expect(page.getByLabel("Status")).toHaveValue("applied");

    await page.getByLabel("Search").fill("nothing-matches");
    await page.getByRole("button", { name: "Apply filters" }).click();
    await expect(page.getByText("No applications match your filters")).toBeVisible();
  });

  test("paginates 20 per page", async ({ page, request }) => {
    const user = await createUser(request);
    const company = await createCompany(request, user, "Batik Cloud");
    for (let i = 1; i <= 25; i++) await createApplication(request, user, { company_id: company.id, role: `Role ${String(i).padStart(2, "0")}` });

    await logInAndWait(page, user);
    await page.goto("/applications");
    const pagination = page.getByRole("navigation", { name: "Pagination" });
    await expect(pagination).toContainText("Page 1 of 2");
    await expect(rows(page)).toHaveCount(20);
    await expect(rows(page).first()).toContainText("Role 25");
    await pagination.getByRole("link", { name: "Next page" }).click();
    await expect(page).toHaveURL(/page=2/);
    await expect(pagination).toContainText("Page 2 of 2");
    await expect(rows(page)).toHaveCount(5);
    await expect(pagination.getByRole("link", { name: "Next page" })).toHaveCount(0);
    await pagination.getByRole("link", { name: "Previous page" }).click();
    await expect(rows(page)).toHaveCount(20);
  });
});

test.describe("create", () => {
  test("creates an application and shows it", async ({ page, request }) => {
    const user = await createUser(request);
    await createCompany(request, user, "Kopi Data");
    await createCompany(request, user, "Batik Cloud");
    await logInAndWait(page, user);

    await page.goto("/applications/new");
    await page.getByLabel("Company").selectOption({ label: "Batik Cloud" });
    await page.getByLabel("Role").fill("  Platform Engineer ");
    await page.getByLabel("Job URL").fill("https://jobs.example.com/platform");
    await page.getByLabel("Minimum salary").fill("15000000");
    await page.getByLabel("Maximum salary").fill("22000000");
    await page.getByRole("button", { name: "Save application" }).click();

    await expect(page).toHaveURL(/\/applications\/\d+$/);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Platform Engineer");
    await expect(page.getByRole("status").filter({ hasText: "Application created" })).toBeVisible();
    await expect(page.getByTestId("status")).toHaveText(STATUS_LABELS.saved);
    await expect(page.getByRole("main").getByText("Batik Cloud", { exact: true }).first()).toBeVisible();

    await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Applications" }).click();
    await expect(rows(page).filter({ hasText: "Platform Engineer" })).toContainText("Batik Cloud");
  });

  test("validates the form and keeps typed values", async ({ page, request }) => {
    const user = await createUser(request);
    await createCompany(request, user, "Kopi Data");
    await logInAndWait(page, user);
    await page.goto("/applications/new");

    await page.getByLabel("Company").selectOption({ label: "Kopi Data" });
    await page.getByLabel("Minimum salary").fill("20000000");
    await page.getByLabel("Maximum salary").fill("10000000");
    await page.getByRole("button", { name: "Save application" }).click();

    await expect(page.getByLabel("Role")).toHaveAttribute("aria-invalid", "true");
    await expect(page.getByLabel("Maximum salary")).toHaveAttribute("aria-invalid", "true");
    await expect(page.getByText("Maximum must be at least the minimum")).toBeVisible();
    await expect(page.getByLabel("Minimum salary")).toHaveValue("20000000");
    await expect(page).toHaveURL(/\/applications\/new$/);
  });
});

test.describe("detail", () => {
  test("offers only allowed transitions and records history", async ({ page, request }) => {
    const user = await createUser(request);
    const company = await createCompany(request, user, "Kopi Data");
    const app = await createApplication(request, user, { company_id: company.id, role: "Backend Engineer" });
    await logInAndWait(page, user);
    await page.goto(`/applications/${app.id}`);

    const moveTo = page.getByLabel("Move to");
    await expect(moveTo.getByRole("option")).toHaveText([STATUS_LABELS.applied, STATUS_LABELS.rejected, STATUS_LABELS.withdrawn]);
    await moveTo.selectOption("applied");
    await page.getByRole("button", { name: "Update status" }).click();
    await expect(page.getByTestId("status")).toHaveText(STATUS_LABELS.applied);
    await expect(page.getByLabel("Move to").getByRole("option")).toHaveText([STATUS_LABELS.screening, STATUS_LABELS.interview, STATUS_LABELS.rejected, STATUS_LABELS.withdrawn]);

    await page.reload();
    const history = page.getByRole("list", { name: "Status history" }).getByRole("listitem");
    await expect(history).toHaveCount(2);
    await expect(history.last()).toContainText("Saved → Applied");
  });

  test("final statuses close the application", async ({ page, request }) => {
    const user = await createUser(request);
    const company = await createCompany(request, user, "Kopi Data");
    const app = await createApplication(request, user, { company_id: company.id, role: "Backend Engineer" });
    await logInAndWait(page, user);
    await page.goto(`/applications/${app.id}`);
    await page.getByLabel("Move to").selectOption("withdrawn");
    await page.getByRole("button", { name: "Update status" }).click();
    await expect(page.getByTestId("status")).toHaveText(STATUS_LABELS.withdrawn);
    await expect(page.getByText("This application is closed")).toBeVisible();
    await expect(page.getByLabel("Move to")).toHaveCount(0);
  });

  test("adds and deletes notes, newest first", async ({ page, request }) => {
    const user = await createUser(request);
    const company = await createCompany(request, user, "Kopi Data");
    const app = await createApplication(request, user, { company_id: company.id, role: "Backend Engineer" });
    await logInAndWait(page, user);
    await page.goto(`/applications/${app.id}`);

    const notes = page.getByRole("list", { name: "Notes" }).getByRole("listitem");
    for (const body of ["Recruiter call went well", "Take-home test due Friday"]) {
      await page.getByLabel("New note").fill(body);
      await page.getByRole("button", { name: "Add note" }).click();
      await expect(notes.filter({ hasText: body })).toBeVisible();
    }
    await expect(notes).toHaveCount(2);
    await expect(notes.first()).toContainText("Take-home test due Friday");
    await expect(page.getByLabel("New note")).toHaveValue("");

    await notes.filter({ hasText: "Recruiter call went well" }).getByRole("button", { name: "Delete note" }).click();
    await expect(notes).toHaveCount(1);
    await page.reload();
    await expect(notes).toHaveCount(1);
  });

  test("deleting asks for confirmation", async ({ page, request }) => {
    const user = await createUser(request);
    const company = await createCompany(request, user, "Kopi Data");
    const app = await createApplication(request, user, { company_id: company.id, role: "Data Engineer" });
    await logInAndWait(page, user);
    await page.goto(`/applications/${app.id}`);

    await page.getByRole("button", { name: "Delete application" }).click();
    const dialog = page.getByRole("alertdialog", { name: 'Delete "Data Engineer"?' });
    await expect(dialog).toBeVisible();
    await dialog.getByRole("button", { name: "Cancel" }).click();
    await expect(dialog).toBeHidden();
    await expect(page).toHaveURL(new RegExp(`/applications/${app.id}$`));

    await page.getByRole("button", { name: "Delete application" }).click();
    await page.getByRole("alertdialog").getByRole("button", { name: "Delete" }).click();
    await expect(page).toHaveURL(/\/applications$/);
    await expect(page.getByRole("status").filter({ hasText: "Application deleted" })).toBeVisible();
    await expect(page.getByText("No applications yet")).toBeVisible();
  });
});
