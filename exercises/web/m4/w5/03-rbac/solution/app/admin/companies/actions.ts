"use server";

import { deleteCompany } from "../../../lib/companies-api";
import { verifySession } from "../../../lib/dal";
import { can } from "../../../lib/permissions";

export async function deleteCompanyAction(companyId: number): Promise<{ ok: true } | { ok: false; message: string }> {
  // Authorize inside the action: hiding the button is not security.
  const session = await verifySession();
  if (!can(session, "companies:manage")) return { ok: false, message: "You don't have permission to do that" };

  await deleteCompany(companyId);
  return { ok: true };
}
