// Page object for /login. See README.md.
import type { Page } from "@playwright/test";

export class LoginPage {
  constructor(readonly page: Page) {}

  // TODO: locators (email, password, submit, alert), goto(), login(email, password)
}
