// A tiny stand-in for the CareerPilot Next.js app, used by the Week 6 Playwright exercises.
// Plain Node.js (no build step) so E2E tests start in milliseconds.
//
//   node m4/w6/_app/server.mjs            → http://localhost:3191
//   PORT=4000 node m4/w6/_app/server.mjs
//
// APP_VARIANT=<name> switches on ONE deliberate bug (used by the graders' mutants). Don't read the
// variants before writing your tests — write tests from the README's behavior list instead.
import { randomUUID } from "node:crypto";
import { createServer } from "node:http";

const PORT = Number(process.env.PORT ?? 3191);
const VARIANT = process.env.APP_VARIANT ?? "";
const bug = (name) => VARIANT === name;

const USER = { email: "sari@example.com", password: "correct-horse", name: "Sari" };
const COMPANIES = [
  { id: 1, name: "Kopi Data" },
  { id: 2, name: "Nusantara Pay" },
  { id: 3, name: "Batik Cloud" },
];
const STATUSES = ["applied", "interview", "offer", "rejected"];
const JOB_TITLES = [
  "Backend Engineer", "Frontend Developer", "Data Engineer", "AI Engineer", "Full-Stack Developer",
  "Platform Engineer", "Mobile Developer", "QA Automation Engineer", "Data Analyst", "Site Reliability Engineer",
  "Machine Learning Engineer", "Product Engineer", "DevOps Engineer", "Security Engineer", "Big Data Engineer",
  "Junior Web Developer", "Cloud Engineer", "Analytics Engineer", "Solutions Engineer", "Staff Data Scientist",
  "React Developer", "Python Developer", "Integration Engineer", "Database Administrator",
];
const JOBS = JOB_TITLES.map((title, i) => ({ id: i + 1, title, company: COMPANIES[i % 3].name }));
const PAGE_SIZE = 10;

/** sessionId → { applications, nextId, flash } — every login gets fresh, isolated data. */
const sessions = new Map();

function seedData() {
  return {
    nextId: 3,
    flash: null,
    applications: [
      { id: 1, companyId: 1, role: "Backend Engineer", status: "applied", salaryMin: 9000000, salaryMax: 14000000 },
      { id: 2, companyId: 2, role: "Data Engineer", status: "interview", salaryMin: null, salaryMax: null },
    ],
  };
}

const escape = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

function parseCookies(req) {
  return Object.fromEntries((req.headers.cookie ?? "").split(";").filter(Boolean).map((p) => p.trim().split("=").map(decodeURIComponent)));
}

async function readForm(req) {
  let body = "";
  for await (const chunk of req) body += chunk;
  return Object.fromEntries(new URLSearchParams(body));
}

function send(res, status, html, headers = {}) {
  res.writeHead(status, { "Content-Type": "text/html; charset=utf-8", ...headers });
  res.end(html);
}

const redirect = (res, location, headers = {}) => {
  res.writeHead(303, { Location: location, ...headers });
  res.end();
};

function takeFlash(session) {
  const flash = session?.flash;
  if (session) session.flash = null;
  return flash;
}

function layout({ title, path, session, body }) {
  const nav = [
    ["/dashboard", "Dashboard"],
    ["/applications", "Applications"],
    ["/jobs", "Jobs"],
  ];
  const links = nav
    .map(([href, label]) => {
      const active = path === href || path.startsWith(`${href}/`);
      const current = active && !bug("nav-no-aria-current") ? ' aria-current="page"' : "";
      return `<li><a href="${href}"${current}>${label}</a></li>`;
    })
    .join("");
  const flash = takeFlash(session);
  return `<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>${escape(title)}</title>
<style>body{font-family:system-ui;margin:2rem} .error{color:#b91c1c} nav ul{display:flex;gap:1rem;list-style:none;padding:0}</style></head>
<body>
<header>
  <nav aria-label="Main"><ul>${links}</ul></nav>
  ${session ? `<form method="post" action="/logout"><button type="submit">Log out</button></form>` : ""}
</header>
<main>
${flash ? `<p role="status">${escape(flash)}</p>` : ""}
${body}
</main>
</body></html>`;
}

function getSession(req) {
  const id = parseCookies(req).session;
  return id ? sessions.get(id) : undefined;
}

function requireSession(req, res, url) {
  const session = getSession(req);
  if (session || bug("no-auth-guard")) return session ?? seedData();
  redirect(res, `/login?next=${encodeURIComponent(url.pathname + url.search)}`);
  return null;
}

function safeNext(value) {
  return typeof value === "string" && /^\/(?![/\\])/.test(value) ? value : "/applications";
}

// ---------- pages ----------
function loginPage({ error, email = "", next = "" }) {
  return layout({
    title: "Log in · CareerPilot",
    path: "/login",
    body: `<h1>Log in</h1>
${error ? `<p role="alert">${escape(error)}</p>` : ""}
<form method="post" action="/login">
  <input type="hidden" name="next" value="${escape(next)}">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" value="${escape(email)}" required>
  <label for="password">Password</label>
  <input id="password" name="password" type="password" required>
  <button type="submit">Log in</button>
</form>`,
  });
}

function companyName(id) {
  return COMPANIES.find((c) => c.id === id)?.name ?? "Unknown";
}

function applicationsPage(session, path) {
  // (variant "created-not-listed": newly created applications are missing from the list)
  const listed = bug("created-not-listed") ? session.applications.filter((a) => a.id < 3) : session.applications;
  const rows = listed
    .map(
      (a) => `<tr><td><a href="/applications/${a.id}">${escape(a.role)}</a></td><td>${escape(companyName(a.companyId))}</td><td>${escape(a.status)}</td></tr>`,
    )
    .join("");
  return layout({
    title: "Applications · CareerPilot",
    path,
    session,
    body: `<h1>Applications</h1>
<p><a href="/applications/new">New application</a></p>
${
  session.applications.length
    ? `<table><caption>${listed.length} applications</caption><thead><tr><th scope="col">Role</th><th scope="col">Company</th><th scope="col">Status</th></tr></thead><tbody>${rows}</tbody></table>`
    : `<p>No applications yet.</p>`
}`,
  });
}

function fieldError(errors, name) {
  return errors[name] ? `<p class="error" id="${name}-error">${escape(errors[name])}</p>` : "";
}

function fieldAttrs(errors, name) {
  return errors[name] ? ` aria-invalid="true" aria-describedby="${name}-error"` : "";
}

function newApplicationPage(session, path, { values = {}, errors = {} } = {}) {
  const options = COMPANIES.map((c) => `<option value="${c.id}"${String(values.company_id) === String(c.id) ? " selected" : ""}>${escape(c.name)}</option>`).join("");
  return layout({
    title: "New application · CareerPilot",
    path,
    session,
    body: `<nav aria-label="Breadcrumb"><a href="/applications">Applications</a> › New</nav>
<h1>New application</h1>
${Object.keys(errors).length ? `<p role="alert">Please fix the errors below</p>` : ""}
<form method="post" action="/applications/new" novalidate>
  <label for="company_id">Company</label>
  <select id="company_id" name="company_id"${fieldAttrs(errors, "company_id")}><option value="">Choose a company</option>${options}</select>
  ${fieldError(errors, "company_id")}
  <label for="role">Role</label>
  <input id="role" name="role" value="${escape(values.role)}"${fieldAttrs(errors, "role")}>
  ${fieldError(errors, "role")}
  <label for="salary_min">Minimum salary</label>
  <input id="salary_min" name="salary_min" inputmode="numeric" value="${escape(values.salary_min)}"${fieldAttrs(errors, "salary_min")}>
  ${fieldError(errors, "salary_min")}
  <label for="salary_max">Maximum salary</label>
  <input id="salary_max" name="salary_max" inputmode="numeric" value="${escape(values.salary_max)}"${fieldAttrs(errors, "salary_max")}>
  ${fieldError(errors, "salary_max")}
  <button type="submit">Save application</button>
</form>
<script>
  document.querySelector("form").addEventListener("submit", (event) => {
    const button = event.target.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = "Saving…";
  });
</script>`,
  });
}

function validateApplication(form) {
  const errors = {};
  if (!COMPANIES.some((c) => String(c.id) === form.company_id)) errors.company_id = "Choose a company";
  if (!(form.role ?? "").trim() && !bug("role-not-required")) errors.role = "Role is required";
  const toNumber = (v) => ((v ?? "").trim() === "" ? null : Number(v));
  const salaryMin = toNumber(form.salary_min);
  const salaryMax = toNumber(form.salary_max);
  if (salaryMin !== null && (!Number.isInteger(salaryMin) || salaryMin < 0)) errors.salary_min = "Enter a whole number";
  if (salaryMax !== null && (!Number.isInteger(salaryMax) || salaryMax < 0)) errors.salary_max = "Enter a whole number";
  if (!errors.salary_min && !errors.salary_max && salaryMin !== null && salaryMax !== null && salaryMin > salaryMax && !bug("salary-range-unchecked")) {
    errors.salary_max = "Maximum must be at least the minimum";
  }
  return { errors, data: { companyId: Number(form.company_id), role: (form.role ?? "").trim(), salaryMin, salaryMax } };
}

function formatSalary(a) {
  if (a.salaryMin === null && a.salaryMax === null) return "Not specified";
  const idr = (n) => `Rp ${n.toLocaleString("id-ID")}`;
  if (a.salaryMin !== null && a.salaryMax !== null) return `${idr(a.salaryMin)} – ${idr(a.salaryMax)}`;
  return a.salaryMin !== null ? `From ${idr(a.salaryMin)}` : `Up to ${idr(a.salaryMax)}`;
}

function applicationDetailPage(session, path, application) {
  const options = STATUSES.map((s) => `<option value="${s}"${s === application.status ? " selected" : ""}>${s}</option>`).join("");
  const title = bug("detail-generic-title") ? "CareerPilot" : `${application.role} · CareerPilot`;
  const crumbHref = bug("breadcrumb-wrong-link") ? "/dashboard" : "/applications";
  return layout({
    title,
    path,
    session,
    body: `<nav aria-label="Breadcrumb"><a href="${crumbHref}">Applications</a> › ${escape(application.role)}</nav>
<h1>${escape(application.role)}</h1>
<dl>
  <dt>Company</dt><dd>${escape(companyName(application.companyId))}</dd>
  <dt>Status</dt><dd data-testid="status">${escape(application.status)}</dd>
  <dt>Salary</dt><dd>${escape(formatSalary(application))}</dd>
</dl>
<form method="post" action="/applications/${application.id}/status">
  <label for="status">Move to</label>
  <select id="status" name="status">${options}</select>
  <button type="submit">Update status</button>
</form>
<button type="button" id="open-delete">Delete</button>
<dialog id="confirm-delete" aria-labelledby="confirm-title">
  <h2 id="confirm-title">Delete "${escape(application.role)}"?</h2>
  <p>This can't be undone.</p>
  <form method="post" action="/applications/${application.id}/delete" id="delete-form">
    <button type="button" id="cancel-delete">Cancel</button>
    <button type="submit">Delete application</button>
  </form>
</dialog>
<script>
  const dialog = document.getElementById("confirm-delete");
  document.getElementById("open-delete").addEventListener("click", () => dialog.showModal());
  document.getElementById("cancel-delete").addEventListener("click", () => {
    ${bug("cancel-deletes") ? 'document.getElementById("delete-form").submit();' : "dialog.close();"}
  });
</script>`,
  });
}

function jobsPage(session, path, url) {
  const q = (url.searchParams.get("q") ?? "").trim();
  const needle = bug("search-case-sensitive") ? q : q.toLowerCase();
  const matches = JOBS.filter((job) => (bug("search-case-sensitive") ? job.title : job.title.toLowerCase()).includes(needle));
  const pages = Math.max(1, Math.ceil(matches.length / PAGE_SIZE));
  const page = Math.min(pages, Math.max(1, Number(url.searchParams.get("page")) || 1));
  const visible = matches.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const link = (p) => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    params.set("page", String(bug("pagination-stuck") ? 1 : p));
    return `/jobs?${params}`;
  };
  return layout({
    title: "Jobs · CareerPilot",
    path,
    session,
    body: `<h1>Jobs</h1>
<form method="get" action="/jobs" role="search">
  <label for="q">Search jobs</label>
  <input id="q" name="q" type="search" value="${escape(q)}">
  <button type="submit">Search</button>
</form>
<p data-testid="result-count">${matches.length} ${matches.length === 1 ? "job" : "jobs"} found</p>
<ul aria-label="Job results">${visible.map((j) => `<li>${escape(j.title)} — ${escape(j.company)}</li>`).join("")}</ul>
<nav aria-label="Pagination">
  <span>Page ${page} of ${pages}</span>
  ${page > 1 ? `<a href="${link(page - 1)}">Previous page</a>` : ""}
  ${page < pages ? `<a href="${link(page + 1)}">Next page</a>` : ""}
</nav>`,
  });
}

function notFoundPage(session, path, message = "Page not found") {
  return layout({ title: "Not found · CareerPilot", path, session, body: `<h1>${escape(message)}</h1><p><a href="/applications">Back to applications</a></p>` });
}

// ---------- router ----------
const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  try {
    if (req.method === "GET" && path === "/health") return send(res, 200, "ok", { "Content-Type": "text/plain" });
    if (req.method === "GET" && path === "/") return redirect(res, "/dashboard");

    if (path === "/login" && req.method === "GET") {
      if (getSession(req)) return redirect(res, "/applications");
      return send(res, 200, loginPage({ next: url.searchParams.get("next") ?? "" }));
    }
    if (path === "/login" && req.method === "POST") {
      const form = await readForm(req);
      if (form.email !== USER.email || form.password !== USER.password) {
        return send(res, 401, loginPage({ error: bug("login-error-hidden") ? "" : "Invalid email or password", email: form.email, next: form.next }));
      }
      const id = randomUUID();
      sessions.set(id, seedData());
      const target = bug("login-ignores-next") ? "/applications" : safeNext(form.next);
      return redirect(res, target, { "Set-Cookie": `session=${id}; HttpOnly; SameSite=Lax; Path=/` });
    }
    if (path === "/logout" && req.method === "POST") {
      const id = parseCookies(req).session;
      if (!bug("logout-keeps-session")) sessions.delete(id);
      return redirect(res, "/login", { "Set-Cookie": bug("logout-keeps-session") ? "x=1; Path=/" : "session=; Max-Age=0; Path=/" });
    }

    const session = requireSession(req, res, url);
    if (!session) return;

    if (req.method === "GET" && path === "/dashboard") {
      return send(res, 200, layout({ title: "Dashboard · CareerPilot", path, session, body: `<h1>Welcome back, ${USER.name}</h1><p>${session.applications.length} active applications</p>` }));
    }
    if (req.method === "GET" && path === "/applications") return send(res, 200, applicationsPage(session, path));
    if (req.method === "GET" && path === "/applications/new") return send(res, 200, newApplicationPage(session, path));
    if (req.method === "POST" && path === "/applications/new") {
      const form = await readForm(req);
      const { errors, data } = validateApplication(form);
      if (Object.keys(errors).length) {
        const values = bug("errors-clear-values") ? {} : form;
        return send(res, 422, newApplicationPage(session, path, { values, errors }));
      }
      const application = { id: session.nextId++, status: "applied", ...data };
      session.applications.push(application);
      if (!bug("no-created-flash")) session.flash = "Application created";
      return redirect(res, `/applications/${application.id}`);
    }

    const detail = path.match(/^\/applications\/(\d+)(?:\/(status|delete))?$/);
    if (detail) {
      const application = session.applications.find((a) => a.id === Number(detail[1]));
      if (!application) {
        if (bug("missing-application-200")) return send(res, 200, applicationsPage(session, "/applications"));
        return send(res, 404, notFoundPage(session, path, "Application not found"));
      }
      if (req.method === "GET" && !detail[2]) return send(res, 200, applicationDetailPage(session, path, application));
      if (req.method === "POST" && detail[2] === "status") {
        const form = await readForm(req);
        if (STATUSES.includes(form.status)) {
          if (!bug("status-not-saved")) application.status = form.status;
          session.flash = "Status updated";
        }
        return redirect(res, `/applications/${application.id}`);
      }
      if (req.method === "POST" && detail[2] === "delete") {
        session.applications = session.applications.filter((a) => a.id !== application.id);
        session.flash = "Application deleted";
        return redirect(res, "/applications");
      }
    }

    if (req.method === "GET" && path === "/jobs") return send(res, 200, jobsPage(session, path, url));
    return send(res, 404, notFoundPage(session, path));
  } catch (error) {
    console.error(error);
    send(res, 500, "Internal Server Error", { "Content-Type": "text/plain" });
  }
});

server.listen(PORT, () => console.log(`CareerPilot mini app on http://localhost:${PORT}${VARIANT ? ` (variant: ${VARIANT})` : ""}`));
