// fetch + async/await. See README.md.

export class ApiError extends Error {}
export class TimeoutError extends Error {}

export async function getJson(fetchImpl, url, options = {}) {
  throw new Error("TODO");
}

export async function getJsonWithTimeout(fetchImpl, url, ms) {
  throw new Error("TODO");
}

export async function loadDashboard(fetchImpl, baseUrl) {
  throw new Error("TODO");
}

export async function loadCompanies(fetchImpl, baseUrl, ids) {
  throw new Error("TODO");
}

export async function withRetry(fn, { attempts = 3, delayMs = 200, sleep } = {}) {
  throw new Error("TODO");
}
