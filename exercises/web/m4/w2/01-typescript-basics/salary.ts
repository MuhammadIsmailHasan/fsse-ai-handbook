// @ts-nocheck — remove this line, then add types until tsc is happy. See README.md.

export function parseSalary(input) {
  const digits = input.replace(/\D/g, "");
  return Number(digits);
}

export function parseRange(text) {
  const parts = text.split("-").map(parseSalary);
  return [parts[0], parts[1]];
}

export function formatAmount(amount, currency = "IDR") {
  if (currency == "IDR") return "Rp " + amount;
  return "$" + amount;
}

export function midpoint(range) {
  return (range[0] + range[1]) / 2;
}
