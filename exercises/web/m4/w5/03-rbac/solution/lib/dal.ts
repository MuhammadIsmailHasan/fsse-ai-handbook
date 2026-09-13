// Provided (simplified): see exercise 02 for the real implementation.
import type { Role } from "./permissions";

export async function verifySession(): Promise<{ userId: number; role: Role }> {
  throw new Error("Not available in tests — mocked");
}
