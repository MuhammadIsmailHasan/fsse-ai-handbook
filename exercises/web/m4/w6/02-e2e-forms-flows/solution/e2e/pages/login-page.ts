import type { Locator, Page } from "@playwright/test";

export const USER = { email: "sari@example.com", password: "correct-horse" };

export class LoginPage {
  readonly email: Locator;
  readonly password: Locator;
  readonly submit: Locator;
  readonly alert: Locator;

  constructor(readonly page: Page) {
    this.email = page.getByLabel("Email");
    this.password = page.getByLabel("Password");
    this.submit = page.getByRole("button", { name: "Log in" });
    this.alert = page.getByRole("alert");
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email = USER.email, password = USER.password) {
    await this.email.fill(email);
    await this.password.fill(password);
    await this.submit.click();
  }
}
