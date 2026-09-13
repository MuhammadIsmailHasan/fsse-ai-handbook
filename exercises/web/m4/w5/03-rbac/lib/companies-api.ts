// Provided.
export async function deleteCompany(companyId: number): Promise<void> {
  const response = await fetch(`${process.env.API_URL}/api/v1/companies/${companyId}`, { method: "DELETE" });
  if (!response.ok) throw new Error(`Delete failed: ${response.status}`);
}
