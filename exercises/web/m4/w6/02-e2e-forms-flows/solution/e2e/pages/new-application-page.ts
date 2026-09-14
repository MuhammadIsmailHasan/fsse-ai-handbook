import type { Locator, Page } from "@playwright/test";

export type ApplicationInput = { company?: string; role?: string; salaryMin?: string; salaryMax?: string };

export class NewApplicationPage {
  readonly company: Locator;
  readonly role: Locator;
  readonly salaryMin: Locator;
  readonly salaryMax: Locator;
  readonly save: Locator;

  constructor(readonly page: Page) {
    this.company = page.getByLabel("Company");
    this.role = page.getByLabel("Role");
    this.salaryMin = page.getByLabel("Minimum salary");
    this.salaryMax = page.getByLabel("Maximum salary");
    this.save = page.getByRole("button", { name: "Save application" });
  }

  async goto() {
    await this.page.goto("/applications/new");
  }

  async fill({ company, role, salaryMin, salaryMax }: ApplicationInput) {
    if (company !== undefined) await this.company.selectOption({ label: company });
    if (role !== undefined) await this.role.fill(role);
    if (salaryMin !== undefined) await this.salaryMin.fill(salaryMin);
    if (salaryMax !== undefined) await this.salaryMax.fill(salaryMax);
  }

  async submit() {
    await this.save.click();
  }
}
