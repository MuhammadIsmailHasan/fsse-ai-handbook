// fetch + async/await — reference solution.

export class ApiError extends Error {
  constructor(status, body) {
    super(`Request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export class TimeoutError extends Error {
  constructor(message = "Request timed out") {
    super(message);
    this.name = "TimeoutError";
  }
}

async function readJson(response) {
  if (response.status === 204) return null;
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export async function getJson(fetchImpl, url, options = {}) {
  const response = await fetchImpl(url, { ...options, headers: { Accept: "application/json", ...options.headers } });
  const body = await readJson(response);
  if (!response.ok) throw new ApiError(response.status, body); // fetch does NOT reject on 4xx/5xx
  return body;
}

export async function getJsonWithTimeout(fetchImpl, url, ms) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try {
    return await getJson(fetchImpl, url, { signal: controller.signal });
  } catch (error) {
    if (controller.signal.aborted) throw new TimeoutError(`Request to ${url} took longer than ${ms} ms`);
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export async function loadDashboard(fetchImpl, baseUrl) {
  const [me, applications, stats] = await Promise.all([
    getJson(fetchImpl, `${baseUrl}/api/v1/me`),
    getJson(fetchImpl, `${baseUrl}/api/v1/applications`),
    getJson(fetchImpl, `${baseUrl}/api/v1/stats`),
  ]);
  return { user: me.data, applications: applications.data, stats: stats.data };
}

export async function loadCompanies(fetchImpl, baseUrl, ids) {
  const results = await Promise.allSettled(ids.map((id) => getJson(fetchImpl, `${baseUrl}/api/v1/companies/${id}`)));
  return {
    companies: results.filter((r) => r.status === "fulfilled").map((r) => r.value.data),
    failedIds: ids.filter((_, i) => results[i].status === "rejected"),
  };
}

const isRetryable = (error) => (error instanceof ApiError && error.status >= 500) || error instanceof TypeError;

export async function withRetry(fn, { attempts = 3, delayMs = 200, sleep = (ms) => new Promise((r) => setTimeout(r, ms)) } = {}) {
  for (let attempt = 1; ; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (!isRetryable(error) || attempt >= attempts) throw error;
      await sleep(delayMs * 2 ** (attempt - 1));
    }
  }
}
