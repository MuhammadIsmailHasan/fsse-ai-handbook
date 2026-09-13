// JavaScript basics & functions — reference solution.

/** @param {string} title */
export function slugify(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** @param {number} rupiah */
function juta(rupiah) {
  // Round to 1 decimal, then drop a trailing ".0" (9.0 → "9").
  return String(Math.round((rupiah / 1_000_000) * 10) / 10);
}

/**
 * @param {number | null | undefined} min
 * @param {number | null | undefined} max
 */
export function salaryLabel(min, max) {
  const hasMin = min !== null && min !== undefined;
  const hasMax = max !== null && max !== undefined;
  if (hasMin && hasMax) {
    if (min > max) throw new RangeError("min must be <= max");
    return min === max ? `Rp ${juta(min)} juta` : `Rp ${juta(min)}–${juta(max)} juta`;
  }
  if (hasMax) return `Up to Rp ${juta(max)} juta`;
  if (hasMin) return `From Rp ${juta(min)} juta`;
  return "Not disclosed";
}

/** @param {unknown} value */
export function isBlank(value) {
  if (value === null || value === undefined) return true;
  return typeof value === "string" && value.trim() === "";
}

/** @param {number} start */
export function createCounter(start = 0) {
  let count = start; // private: only these functions can see it
  return {
    increment: () => ++count,
    decrement: () => --count,
    reset: () => (count = start),
    value: () => count,
  };
}

/**
 * @template {unknown[]} A
 * @param {(...args: A) => void} fn
 * @param {number} waitMs
 */
export function debounce(fn, waitMs) {
  /** @type {ReturnType<typeof setTimeout> | undefined} */
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), waitMs);
  };
}
