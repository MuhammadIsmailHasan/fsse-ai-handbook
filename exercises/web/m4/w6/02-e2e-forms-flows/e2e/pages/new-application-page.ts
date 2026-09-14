// Page object for /applications/new. See README.md.
import type { Page } from "@playwright/test";

export class NewApplicationPage {
  constructor(readonly page: Page) {}

  // TODO: locators, goto(), fill({ company, role, salaryMin, salaryMax }), submit()
}
