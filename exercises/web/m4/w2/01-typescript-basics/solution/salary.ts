export type Currency = "IDR" | "USD";
export type SalaryRange = readonly [min: number | null, max: number | null];

export function parseSalary(input: string): number | null {
  const digits = input.replace(/\D/g, "");
  return digits === "" ? null : Number(digits); // Number("") is 0 — a hidden bug in the JS version
}

export function parseRange(text: string): SalaryRange {
  const amounts = text
    .split(/\s[-–]\s|\s*[-–]\s*(?=\D*\d)/)
    .map(parseSalary)
    .filter((amount): amount is number => amount !== null);
  if (amounts.length === 0) return [null, null];
  const [min, max = min] = amounts as [number, number?];
  return [min, max];
}

function groupDigits(amount: number, separator: string): string {
  return String(Math.round(amount)).replace(/\B(?=(\d{3})+(?!\d))/g, separator);
}

export function formatAmount(amount: number, currency: Currency = "IDR"): string {
  return currency === "IDR" ? `Rp ${groupDigits(amount, ".")}` : `$${groupDigits(amount, ",")}`;
}

export function midpoint([min, max]: SalaryRange): number | null {
  if (min === null || max === null) return null;
  return Math.floor((min + max) / 2);
}
