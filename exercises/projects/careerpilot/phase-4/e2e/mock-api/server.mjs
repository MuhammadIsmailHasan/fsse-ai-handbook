// Mock CareerPilot Phase 2 API — follows the Phase 2 contract (same paths, bodies and errors), in memory.
// The acceptance tests run your web app against this server so results don't depend on your API's data.
// Your app should work the same against your real Flask API.
//
//   node e2e/mock-api/server.mjs            → http://localhost:5093/api/v1
import { randomBytes, randomUUID } from "node:crypto";
import { createServer } from "node:http";

const PORT = Number(process.env.MOCK_API_PORT ?? 5093);
const STATUSES = ["saved", "applied", "screening", "interview", "offer", "accepted", "rejected", "withdrawn"];
const FINAL = new Set(["accepted", "rejected", "withdrawn"]);
const TRANSITIONS = {
  saved: ["applied", "rejected", "withdrawn"],
  applied: ["screening", "interview", "rejected", "withdrawn"],
  screening: ["interview", "rejected", "withdrawn"],
  interview: ["offer", "rejected", "withdrawn"],
  offer: ["accepted", "rejected", "withdrawn"],
  accepted: [],
  rejected: [],
  withdrawn: [],
};

const db = { users: [], tokens: new Map(), companies: [], applications: [], notes: [], history: [], ids: { user: 1, company: 1, application: 1, note: 1 } };
const now = () => new Date().toISOString();
const today = () => now().slice(0, 10);

class HttpError extends Error {
  constructor(status, code, message, fields) {
    super(message);
    Object.assign(this, { status, code, fields });
  }
}
const validation = (fields) => new HttpError(422, "validation_failed", "Validation failed", fields);
const notFound = () => new HttpError(404, "not_found", "Resource not found");

function send(res, status, body, headers = {}) {
  res.writeHead(status, { "X-Request-ID": randomUUID(), ...(body === undefined ? {} : { "Content-Type": "application/json" }), ...headers });
  res.end(body === undefined ? undefined : JSON.stringify(body));
}

async function readJson(req) {
  let raw = "";
  for await (const chunk of req) raw += chunk;
  if (!raw) return {};
  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) throw new Error();
    return parsed;
  } catch {
    throw validation({ _schema: ["Request body must be a JSON object."] });
  }
}

function allowOnly(body, allowed) {
  const unknown = Object.keys(body).filter((k) => !allowed.includes(k));
  if (unknown.length) throw validation(Object.fromEntries(unknown.map((k) => [k, ["Unknown field."]])));
}

function authenticate(req) {
  const header = req.headers.authorization ?? "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : null;
  const userId = token ? db.tokens.get(token) : undefined;
  if (!userId) throw new HttpError(401, "unauthorized", "Missing or invalid token");
  return db.users.find((u) => u.id === userId);
}

const str = (v) => (typeof v === "string" ? v.trim() : v);
const isInt = (v) => Number.isInteger(v) && v >= 0;

function companyDto(c) {
  return { id: c.id, name: c.name, website: c.website, created_at: c.created_at };
}

function applicationDto(a) {
  const company = db.companies.find((c) => c.id === a.company_id);
  return {
    id: a.id,
    company: { id: company.id, name: company.name },
    role: a.role,
    job_url: a.job_url,
    salary_min: a.salary_min,
    salary_max: a.salary_max,
    status: a.status,
    applied_on: a.applied_on,
    created_at: a.created_at,
    updated_at: a.updated_at,
  };
}

function ownApplication(user, id) {
  const app = db.applications.find((a) => a.id === Number(id) && a.user_id === user.id);
  if (!app) throw notFound();
  return app;
}

function validateApplicationFields(body, user, { partial, existing }) {
  const fields = {};
  const out = {};
  if (!partial || "company_id" in body) {
    if (!Number.isInteger(body.company_id) || !db.companies.some((c) => c.id === body.company_id && c.user_id === user.id)) fields.company_id = ["Company not found."];
    else out.company_id = body.company_id;
  }
  if (!partial || "role" in body) {
    const role = str(body.role);
    if (typeof role !== "string" || role.length < 1 || role.length > 200) fields.role = ["Length must be between 1 and 200."];
    else out.role = role;
  }
  if ("job_url" in body) {
    const url = body.job_url === null || body.job_url === "" ? null : str(body.job_url);
    if (url !== null && (typeof url !== "string" || !/^https?:\/\/\S+$/.test(url))) fields.job_url = ["Not a valid URL."];
    else out.job_url = url;
  }
  for (const key of ["salary_min", "salary_max"]) {
    if (key in body) {
      if (body[key] !== null && !isInt(body[key])) fields[key] = ["Must be greater than or equal to 0."];
      else out[key] = body[key];
    }
  }
  if ("applied_on" in body) {
    if (body.applied_on !== null && !/^\d{4}-\d{2}-\d{2}$/.test(body.applied_on)) fields.applied_on = ["Not a valid date."];
    else out.applied_on = body.applied_on;
  }
  const min = "salary_min" in out ? out.salary_min : existing?.salary_min ?? null;
  const max = "salary_max" in out ? out.salary_max : existing?.salary_max ?? null;
  if (!fields.salary_min && !fields.salary_max && min !== null && max !== null && min > max) fields.salary_max = ["Must be greater than or equal to salary_min."];
  if (Object.keys(fields).length) throw validation(fields);
  return out;
}

async function route(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname.replace(/\/+$/, "") || "/";
  const method = req.method;

  if (path === "/health/live" || path === "/health/ready") return send(res, 200, { status: "ok" });
  if (!path.startsWith("/api/v1")) throw notFound();
  const p = path.slice("/api/v1".length);

  // ---- auth
  if (p === "/auth/register" && method === "POST") {
    const body = await readJson(req);
    allowOnly(body, ["email", "password", "name"]);
    const fields = {};
    const email = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
    const name = str(body.name);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) fields.email = ["Not a valid email address."];
    if (typeof body.password !== "string" || body.password.length < 8 || body.password.length > 128) fields.password = ["Length must be between 8 and 128."];
    if (typeof name !== "string" || name.length < 1 || name.length > 100) fields.name = ["Length must be between 1 and 100."];
    if (Object.keys(fields).length) throw validation(fields);
    if (db.users.some((u) => u.email === email)) throw new HttpError(409, "email_taken", "Email is already registered");
    const user = { id: db.ids.user++, email, name, password: body.password };
    db.users.push(user);
    return send(res, 201, { data: { id: user.id, email, name } });
  }
  if (p === "/auth/login" && method === "POST") {
    const body = await readJson(req);
    const email = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
    const user = db.users.find((u) => u.email === email);
    if (!user || user.password !== body.password) throw new HttpError(401, "invalid_credentials", "Invalid email or password");
    const token = `cpt_${randomBytes(24).toString("hex")}`;
    db.tokens.set(token, user.id);
    return send(res, 200, { data: { access_token: token, token_type: "Bearer", expires_in: 3600 } });
  }

  const user = authenticate(req);

  if (p === "/me" && method === "GET") return send(res, 200, { data: { id: user.id, email: user.email, name: user.name } });

  // ---- companies
  if (p === "/companies" && method === "GET") {
    const list = db.companies.filter((c) => c.user_id === user.id).sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
    return send(res, 200, { data: list.map(companyDto) });
  }
  if (p === "/companies" && method === "POST") {
    const body = await readJson(req);
    allowOnly(body, ["name", "website"]);
    const name = str(body.name);
    const website = body.website === undefined || body.website === null || body.website === "" ? null : str(body.website);
    const fields = {};
    if (typeof name !== "string" || name.length < 1 || name.length > 200) fields.name = ["Length must be between 1 and 200."];
    if (website !== null && !/^https?:\/\/\S+$/.test(website)) fields.website = ["Not a valid URL."];
    if (Object.keys(fields).length) throw validation(fields);
    if (db.companies.some((c) => c.user_id === user.id && c.name.toLowerCase() === name.toLowerCase())) throw new HttpError(409, "company_exists", "Company already exists");
    const company = { id: db.ids.company++, user_id: user.id, name, website, created_at: now() };
    db.companies.push(company);
    return send(res, 201, { data: companyDto(company) }, { Location: `/api/v1/companies/${company.id}` });
  }
  let m = p.match(/^\/companies\/(\d+)$/);
  if (m) {
    const company = db.companies.find((c) => c.id === Number(m[1]) && c.user_id === user.id);
    if (!company) throw notFound();
    if (method === "GET") return send(res, 200, { data: companyDto(company) });
    if (method === "DELETE") {
      if (db.applications.some((a) => a.company_id === company.id)) throw new HttpError(409, "company_in_use", "Company has applications");
      db.companies = db.companies.filter((c) => c !== company);
      return send(res, 204);
    }
    if (method === "PATCH") {
      const body = await readJson(req);
      allowOnly(body, ["name", "website"]);
      if ("name" in body) company.name = str(body.name);
      if ("website" in body) company.website = body.website || null;
      return send(res, 200, { data: companyDto(company) });
    }
    throw new HttpError(405, "method_not_allowed", "Method not allowed");
  }

  // ---- applications
  if (p === "/applications" && method === "GET") {
    const status = url.searchParams.get("status");
    const companyId = url.searchParams.get("company_id");
    const q = (url.searchParams.get("q") ?? "").trim().toLowerCase();
    const page = Number(url.searchParams.get("page") ?? 1);
    const perPage = Number(url.searchParams.get("per_page") ?? 20);
    const fields = {};
    if (status && !STATUSES.includes(status)) fields.status = ["Must be one of: " + STATUSES.join(", ") + "."];
    if (!Number.isInteger(page) || page < 1) fields.page = ["Must be greater than or equal to 1."];
    if (!Number.isInteger(perPage) || perPage < 1 || perPage > 100) fields.per_page = ["Must be between 1 and 100."];
    if (companyId && !/^\d+$/.test(companyId)) fields.company_id = ["Not a valid integer."];
    if (Object.keys(fields).length) throw validation(fields);
    const all = db.applications
      .filter((a) => a.user_id === user.id)
      .filter((a) => !status || a.status === status)
      .filter((a) => !companyId || a.company_id === Number(companyId))
      .filter((a) => !q || a.role.toLowerCase().includes(q))
      .sort((a, b) => b.created_at.localeCompare(a.created_at) || b.id - a.id);
    const data = all.slice((page - 1) * perPage, page * perPage).map(applicationDto);
    return send(res, 200, { data, meta: { page, per_page: perPage, total: all.length } });
  }
  if (p === "/applications" && method === "POST") {
    const body = await readJson(req);
    allowOnly(body, ["company_id", "role", "job_url", "salary_min", "salary_max", "applied_on"]);
    const values = validateApplicationFields(body, user, { partial: false });
    const app = { id: db.ids.application++, user_id: user.id, job_url: null, salary_min: null, salary_max: null, applied_on: null, ...values, status: "saved", created_at: now(), updated_at: now() };
    db.applications.push(app);
    db.history.push({ application_id: app.id, from_status: null, to_status: "saved", changed_at: now() });
    return send(res, 201, { data: applicationDto(app) }, { Location: `/api/v1/applications/${app.id}` });
  }
  m = p.match(/^\/applications\/(\d+)(?:\/(status|history|notes))?$/);
  if (m) {
    const app = ownApplication(user, m[1]);
    const sub = m[2];
    if (!sub && method === "GET") return send(res, 200, { data: applicationDto(app) });
    if (!sub && method === "PATCH") {
      const body = await readJson(req);
      if ("status" in body) throw validation({ status: ["Use POST /applications/<id>/status."] });
      allowOnly(body, ["company_id", "role", "job_url", "salary_min", "salary_max", "applied_on"]);
      Object.assign(app, validateApplicationFields(body, user, { partial: true, existing: app }), { updated_at: now() });
      return send(res, 200, { data: applicationDto(app) });
    }
    if (!sub && method === "DELETE") {
      db.applications = db.applications.filter((a) => a !== app);
      db.notes = db.notes.filter((n) => n.application_id !== app.id);
      db.history = db.history.filter((h) => h.application_id !== app.id);
      return send(res, 204);
    }
    if (sub === "status" && method === "POST") {
      const body = await readJson(req);
      allowOnly(body, ["status"]);
      if (!STATUSES.includes(body.status)) throw validation({ status: ["Must be one of: " + STATUSES.join(", ") + "."] });
      if (!TRANSITIONS[app.status].includes(body.status)) throw new HttpError(409, "invalid_transition", `Cannot move from ${app.status} to ${body.status}`);
      db.history.push({ application_id: app.id, from_status: app.status, to_status: body.status, changed_at: now() });
      app.status = body.status;
      if (body.status === "applied" && !app.applied_on) app.applied_on = today();
      app.updated_at = now();
      return send(res, 200, { data: applicationDto(app) });
    }
    if (sub === "history" && method === "GET") {
      const items = db.history.filter((h) => h.application_id === app.id).map(({ from_status, to_status, changed_at }) => ({ from_status, to_status, changed_at }));
      return send(res, 200, { data: items });
    }
    if (sub === "notes" && method === "GET") {
      const items = db.notes.filter((n) => n.application_id === app.id).sort((a, b) => b.id - a.id).map(({ id, body, created_at }) => ({ id, body, created_at }));
      return send(res, 200, { data: items });
    }
    if (sub === "notes" && method === "POST") {
      const body = await readJson(req);
      allowOnly(body, ["body"]);
      const text = str(body.body);
      if (typeof text !== "string" || text.length < 1 || text.length > 5000) throw validation({ body: ["Length must be between 1 and 5000."] });
      const note = { id: db.ids.note++, application_id: app.id, body: text, created_at: now() };
      db.notes.push(note);
      return send(res, 201, { data: { id: note.id, body: note.body, created_at: note.created_at } });
    }
    throw new HttpError(405, "method_not_allowed", "Method not allowed");
  }
  m = p.match(/^\/notes\/(\d+)$/);
  if (m && method === "DELETE") {
    const note = db.notes.find((n) => n.id === Number(m[1]));
    const owner = note && db.applications.find((a) => a.id === note.application_id && a.user_id === user.id);
    if (!owner) throw notFound();
    db.notes = db.notes.filter((n) => n !== note);
    return send(res, 204);
  }

  if (p === "/stats" && method === "GET") {
    const mine = db.applications.filter((a) => a.user_id === user.id);
    const by_status = Object.fromEntries(STATUSES.map((s) => [s, mine.filter((a) => a.status === s).length]));
    return send(res, 200, { data: { total: mine.length, active: mine.filter((a) => !FINAL.has(a.status)).length, by_status } });
  }

  throw notFound();
}

createServer((req, res) => {
  route(req, res).catch((error) => {
    if (error instanceof HttpError) {
      return send(res, error.status, { error: { code: error.code, message: error.message, ...(error.fields ? { fields: error.fields } : {}) } });
    }
    console.error(error);
    send(res, 500, { error: { code: "internal_error", message: "Internal server error" } });
  });
}).listen(PORT, () => console.log(`Mock CareerPilot API on http://localhost:${PORT}/api/v1`));
