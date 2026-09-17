---
title: "REST Concepts & GET Endpoints"
summary: Design resource-oriented APIs and build GET endpoints that filter, sort and paginate safely — with consistent response envelopes clients love.
type: lesson
source: core
sourceRef: "M2 · W5 · L1"
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: optional }
durationMinutes: 180
tags: [rest, api-design, pagination, filtering, flask]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **REST** means in practice: resources, representations, methods, statelessness
- Designing **URLs** and naming conventions
- **Safe** and **idempotent** methods
- GET endpoints for **collections** and **single resources**
- **Filtering**, **sorting** (with whitelists), **pagination** (offset and keyset) and response **envelopes**
- Versioning and caching basics

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **REST** | A style where data is resources with URLs, used through standard HTTP methods | Gaya desain API |
| **Resource** | One thing your API exposes (a job, a user) | Objek yang disediakan API |
| **Endpoint** | One URL + method your API answers | Satu alamat API |
| **Safe method** | A request that changes nothing (`GET`) | Tidak mengubah data |
| **Idempotent** | Doing it twice has the same result as once (`PUT`, `DELETE`) | Diulang hasilnya sama |
| **Stateless** | The server keeps no memory between requests; each one carries what it needs | Tanpa ingatan antar permintaan |
| **Envelope** | The fixed shape every response uses (`data`, `meta`, `error`) | Bentuk balasan seragam |
| **Pagination** | Returning results page by page | Membagi hasil per halaman |
| **Keyset pagination** | Paging with "after this item" instead of "skip 5,000 rows" | Paging berbasis penanda |
| **Whitelist** | The fixed list of values you allow (sort fields) | Daftar nilai yang diizinkan |

## 🧠 The big idea

:term[REST]{bahasa="REST — gaya desain API yang memodelkan data sebagai resource dengan URL, dimanipulasi lewat method HTTP standar"} treats your API like a **library catalogue**:

- Every thing — a book, a member — is a **resource** with an address: `/books/42`.
- You act on those addresses with a small set of **standard verbs**: look (`GET`), add (`POST`), replace (`PUT`), change (`PATCH`), remove (`DELETE`).
- Anyone who knows HTTP can then guess how to use your API **without reading your code**.

## ❓ Why it matters

Frontends, mobile apps, partners and other services all talk to your backend. A predictable design means fewer bugs, less documentation to write, easier caching, and clients that can be built at the same time as the backend.

Inconsistent design looks like this:

```text
GET  /getJobs?cityName=Jakarta
POST /job/create
GET  /api/job_detail?jobid=42
POST /deleteJobById
GET  /jobs/list?page=1&pageSize=100000
```

Every endpoint now needs its own documentation, clients guess wrong, `GET` requests change data — and browsers happily cache or pre-fetch those — and someone asks for 100,000 rows at once.

## 📖 Step by step

### 1. Resources and URLs

| Rule | ✅ | ❌ |
|---|---|---|
| Nouns, not verbs | `/api/v1/applications` | `/api/v1/getApplications` |
| Plural collections | `/applications`, `/applications/42` | `/application/42` |
| Nest only for ownership | `/applications/42/interviews` | `/users/7/applications/42/interviews/3/notes` |
| Lowercase, hyphens | `/job-listings` | `/JobListings`, `/job_listings` |
| Version in the path (or header) | `/api/v1/...` | breaking changes with no version |
| Actions that don't fit CRUD | `POST /applications/42/status` or `POST /payments/9/refund` | `GET /refund?id=9` |

### 2. Methods: safe and idempotent

These two promises are what let networks retry safely: a lift button you can press twice without calling two lifts.

| Method | Use | Safe (no changes)? | Idempotent (same effect if repeated)? |
|---|---|---|---|
| `GET` | read | ✅ | ✅ |
| `POST` | create / action | ❌ | ❌ (unless you add idempotency keys) |
| `PUT` | replace entirely | ❌ | ✅ |
| `PATCH` | partial update | ❌ | usually ✅ in practice |
| `DELETE` | remove | ❌ | ✅ |

**Safe** methods must never change data: crawlers, browsers and caches call `GET` freely. **Idempotent** methods can be retried after a network timeout without doing the change twice.

### 3. Statelessness

Each request carries everything needed (auth token, parameters). The server doesn't remember "the previous page you looked at" — which is why pagination parameters and tokens are sent every time (and why horizontal scaling works — Architecture Stage B).

### 4. Response envelopes

Pick one shape and use it everywhere:

```json
{
  "data": [ { "id": 42, "title": "Backend Engineer" } ],
  "meta": { "page": 2, "per_page": 20, "total": 134, "total_pages": 7 },
  "links": { "self": "/api/v1/jobs?page=2", "next": "/api/v1/jobs?page=3", "prev": "/api/v1/jobs?page=1" }
}
```

```json
{ "data": { "id": 42, "title": "Backend Engineer" } }
```

```json
{ "error": { "code": "job_not_found", "message": "Job 42 not found" } }
```

Clients can write **one** generic handler for success, pagination and errors.

### 5. Filtering

```text
GET /api/v1/jobs?city=jakarta&remote=true&min_salary=10000000&q=engineer
```

- Validate and **convert** every parameter (`remote` must be `true`/`false`; `min_salary` an integer ≥ 0).
- Unknown or invalid values → `422` with a clear message (don't silently ignore typos like `?reomte=true`).
- Translate filters into **parameterized** query conditions in the repository.

### 6. Sorting with a whitelist

```text
GET /api/v1/jobs?sort=-salary_max,title
```

`-` means descending. **Never** pass user input straight into `ORDER BY`:

```python
SORTABLE = {"posted_on": Job.posted_on, "salary_max": Job.salary_max, "title": Job.title}

def order_by_clauses(sort: str):
    clauses = []
    for part in sort.split(","):
        descending = part.startswith("-")
        column = SORTABLE.get(part.lstrip("-"))
        if column is None:
            raise ValidationFailed({"sort": f"unknown field {part!r}"})
        clauses.append(column.desc() if descending else column.asc())
    clauses.append(Job.id.desc())           # always a unique tie-breaker for stable pages
    return clauses
```

### 7. Offset pagination

```python
per_page = min(max(per_page, 1), 100)       # enforce limits
stmt = base.order_by(*clauses).limit(per_page).offset((page - 1) * per_page)
total = db.session.scalar(select(func.count()).select_from(base.subquery()))
```

- ✅ simple; "jump to page 7"; total counts
- ❌ `OFFSET 100000` is slow (the database still walks those rows); rows shift when new data arrives

### 8. Keyset (cursor) pagination

Offset paging is asking the librarian to count past 5,000 books every time; keyset paging is saying "continue from this book" — much faster, and nothing is skipped when new rows arrive.

```text
GET /api/v1/jobs?limit=20                      → ..., "next_cursor": "eyJwIjoiMjAyNi0wOS0xMCIsImkiOjQyfQ"
GET /api/v1/jobs?limit=20&cursor=eyJwIjoiMjAy…
```

```python
# cursor decodes to (last_posted_on, last_id)
stmt = (
    select(Job)
    .where(tuple_(Job.posted_on, Job.id) < (last_posted_on, last_id))
    .order_by(Job.posted_on.desc(), Job.id.desc())
    .limit(limit)
)
```

- ✅ fast at any depth (uses the index on `(posted_on, id)`), stable with inserts
- ❌ no "jump to page 37", no cheap total count
- Encode the cursor (e.g. base64 JSON) so clients treat it as **opaque**

Infinite scroll feeds and large exports use keyset; admin tables with page numbers often use offset.

### 9. Single resource

```python
@jobs_bp.get("/<int:job_id>")
def get_job(job_id: int):
    job = job_service().get(job_id)            # raises JobNotFound → 404 via the error handler
    return {"data": JobSchema().dump(job)}
```

### 10. Caching headers (a preview)

`GET` responses can include `Cache-Control` and `ETag` so clients and CDNs avoid re-downloading unchanged data (`304 Not Modified`). Never cache private, per-user responses publicly.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| REST (resources + methods) | predictable, cacheable, great tooling | awkward for complex actions or deeply nested reads |
| GraphQL (Architecture Stage F) | clients choose fields, fewer round trips | caching and authorization are harder; N+1 risks |
| RPC style (`POST /doSomething`) | simple for actions | inconsistent, poor caching |
| Offset pagination | page numbers, totals | slow deep pages, unstable |
| Keyset pagination | fast, stable | no random page access |
| Envelopes (`data/meta/error`) | consistent clients | slightly bigger payloads |

- ✅ REST for most CRUD-style business APIs.
- ✅ Keyset pagination for large or append-heavy collections (feeds, logs, listings).
- 🚫 Don't return unbounded collections — always paginate.
- 🚫 Don't use `GET` for anything that changes state.
- 🚫 Don't expose database column names or internal ids you may want to change without versioning.

## ⚠️ Common mistakes

- Verbs in URLs; singular/plural mix.
- `ORDER BY` built from raw query strings (SQL injection + crashes).
- No maximum `per_page`.
- Pagination without a unique tie-breaker → rows repeat or disappear between pages.
- Returning `200` with `{"error": ...}`.

:::revoshop
In RevoShop's `app/routes/products.py`, the list endpoint reads `ProductQuerySchema` query params (`name`, `category_id`, `seller_id`, `min_price`, `max_price`, `sort_by`, `order`, `page`, `limit`) and returns `make_response(..., pagination=paginate_meta(paginated))`. Open `app/schemas/product_schema.py` and `app/utils/http.py`: (1) Is `sort_by` restricted to a whitelist (e.g. `validate.OneOf`)? (2) Is `limit` capped? (3) What does your pagination metadata contain? (4) Is there a unique tie-breaker in the ordering? Compare your envelope (`make_response`) with this lesson's — would a frontend developer find it consistent across every endpoint?
:::

## 🏆 Best practices

- [ ] **Plural nouns**, lowercase-hyphen paths, `/api/v1` versioning.
- [ ] `GET` is **safe**; design writes to be **idempotent** where possible.
- [ ] One **consistent envelope** for data, pagination metadata and errors.
- [ ] **Validate and convert** all query parameters; unknown/invalid → `422`.
- [ ] **Whitelist** sortable/filterable fields; always add a unique **tie-breaker** to ordering.
- [ ] Enforce a **maximum page size** (e.g. 100) and a sensible default (e.g. 20).
- [ ] Use **keyset pagination** for large or fast-growing collections; opaque cursors.
- [ ] Index columns used in filters and sort orders (Week 2 lesson 06).
- [ ] Return **404** for resources that don't exist **or** aren't visible to the caller.
- [ ] Document parameters and responses with OpenAPI (lesson 07).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a frontend developer friend why your job list endpoint returns at most 100 items per request, and the difference between page-number pagination and "load more" cursor pagination.

## 📐 Design it

Design `GET /api/v1/applications` for CareerPilot: filters (status — multiple allowed, company, applied date range, text search on role), sorting options, pagination style, response envelope, validation errors, and the database indexes the query needs. Show one example request and response.

:::quiz
Show a possible design

**Request:** `GET /api/v1/applications?status=applied,interview&company_id=12&applied_from=2026-08-01&applied_to=2026-09-13&q=engineer&sort=-applied_on&limit=20&cursor=…`

**Rules:** `status` values from the allowed set; dates ISO format with `applied_from <= applied_to`; `q` ≥ 2 characters; `sort` in {`applied_on`, `-applied_on`, `company`, `status`} with `id` tie-breaker; `limit` 1–100 (default 20); keyset cursor for the default sort (offset allowed for other sorts in an admin view).

**Response:**
```json
{
  "data": [{"id": 88, "company": {"id": 12, "name": "Kopi Data"}, "role_title": "Analytics Engineer", "status": "interview", "applied_on": "2026-09-02"}],
  "meta": {"limit": 20, "next_cursor": "eyJkIjoiMjAyNi0wOS0wMiIsImkiOjg4fQ"}
}
```

**Errors:** `422 {"error": {"code": "invalid_query", "fields": {"status": "unknown value 'hired'"}}}`

**Indexes:** `(user_id, applied_on DESC, id DESC)` for the default listing; `(user_id, status)`; trigram index on `role_title` if search becomes slow.
:::

### 📝 Self-review checklist

- [ ] Every parameter is validated with a clear error
- [ ] Sorting is whitelisted with a tie-breaker
- [ ] Page size is limited; pagination style fits the use case
- [ ] Indexes match the default query

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w5/01-rest-get" ai="no-ai" title="Filter, sort and paginate job listings"}
Implement `GET /api/v1/jobs` and `GET /api/v1/jobs/<id>` on real PostgreSQL: validated filters, whitelisted multi-field sorting with a tie-breaker, offset pagination with `meta` and `links`, and **keyset** pagination with an opaque cursor. Tests compare pages against the seed data and try injection-style sort parameters.
:::

:::hints
- Parse and validate query params into a plain dict first; build the query second.
- `tuple_(Job.posted_on, Job.id) < (posted_on, job_id)` for keyset "older than".
- Encode cursors with `base64.urlsafe_b64encode(json.dumps(...).encode())`; reject cursors that don't decode.
- The tie-breaker for every sort is `id` in the **same direction as the last sort field**.
:::

### 🏆 Stretch goal

Add an `ETag` header (hash of the response body) and return `304 Not Modified` when the request's `If-None-Match` matches.

## ✅ Quick check

:::quiz
What's the difference between safe and idempotent?

Safe methods don't change server state (GET). Idempotent methods may change state, but repeating them has the same effect as doing them once (PUT, DELETE).
:::

:::quiz
Why must pagination order include a unique column like `id`?

Without a unique tie-breaker, rows with equal sort values can appear in any order, so they may repeat or be skipped between pages.
:::

:::quiz
Why whitelist sort fields instead of passing `?sort=` into the query?

User input in `ORDER BY` enables SQL injection or crashes, and exposes columns (or unindexed sorts) you never intended to support.
:::


## 📚 Keep learning

- [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Use The Index, Luke: Paging through results (keyset)](https://use-the-index-luke.com/no-offset)
