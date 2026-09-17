---
title: "API Documentation with OpenAPI (flask-smorest)"
summary: Generate accurate, interactive API docs from your code — OpenAPI specs, Swagger UI, documented schemas, errors and security — so docs never drift from reality.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: optional }
durationMinutes: 120
tags: [openapi, swagger, documentation, flask-smorest, api-design, bonus]
lastReviewed: 2026-09
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What the **OpenAPI** specification is and what it enables (docs, client generation, testing, mocking)
- **Code-first** vs **design-first** documentation
- Documenting Flask APIs with **flask-smorest**: `@blp.arguments`, `@blp.response`, `@blp.alt_response`, docstrings, tags
- Describing **security** (Bearer JWT), **errors** and **examples**
- Keeping docs honest: testing the spec in CI

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **OpenAPI** | A standard file describing every endpoint of an API | Standar deskripsi API |
| **Spec** | That file itself (JSON or YAML) | Berkas deskripsi |
| **Swagger UI** | A web page that reads the spec so people can try the API | Halaman coba API |
| **Code-first** | The spec is generated from your code and schemas | Spesifikasi dari kode |
| **Design-first** | The spec is written first, then the code follows | Spesifikasi dulu, kode menyusul |
| **flask-smorest** | The Flask library that produces the spec from your routes and schemas | Pustaka penghasil spesifikasi |
| **Tag** | A group of endpoints in the docs (jobs, auth) | Pengelompokan endpoint |
| **Security scheme** | How the docs describe authentication (Bearer JWT) | Cara autentikasi didokumentasikan |
| **Contract** | The agreement between backend and clients about requests and responses | Kesepakatan API |

## 🧠 The big idea

:term[OpenAPI]{bahasa="OpenAPI — standar format (JSON/YAML) untuk mendeskripsikan endpoint, parameter, dan respons sebuah API"} is a **machine-readable menu** for your API: every dish (endpoint), its ingredients (parameters and body), what arrives at the table (responses), and the allergy warnings (errors, authentication).

People read it through tools like **Swagger UI**; machines use it to generate client code, mock servers and tests.

The best menu is printed **from the kitchen's actual recipes**, so it can't advertise dishes the kitchen no longer makes. That's code-first documentation.

## ❓ Why it matters

Frontend, mobile and partner teams need to know exactly how to call your API. Hand-written docs in a wiki go stale within weeks. A spec generated from the same schemas that already validate your requests stays true, and tools can use it automatically.

Without it (or with hand-written docs):

- The README says `POST /jobs` takes `name`; the code expects `title` → hours of frontend debugging.
- Nobody knows which errors an endpoint returns, so clients show "Something went wrong" for everything.
- New teammates read controller code to discover the parameters.
- A recruiter opening your portfolio API has no way to try it.

## 📖 Step by step

### 1. The spec's main parts

```yaml
openapi: 3.0.3
info: { title: CareerPilot API, version: v1 }
paths:
  /api/v1/companies:
    post:
      tags: [companies]
      summary: Create a company
      security: [{ BearerAuth: [] }]
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/CompanyCreate' }
      responses:
        '201': { description: Created, content: { application/json: { schema: { $ref: '#/components/schemas/Company' } } } }
        '409': { description: A company with this name already exists }
components:
  schemas: { CompanyCreate: {…}, Company: {…} }
  securitySchemes:
    BearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
```

### 2. Code-first vs design-first

| Approach | How | Best for |
|---|---|---|
| **Code-first** | generate the spec from code (flask-smorest, FastAPI) | small/medium teams, fast iteration — this lesson |
| **Design-first** | write the spec first, review it, then implement (and generate stubs) | public APIs, many consumers, contract agreements |

### 3. flask-smorest setup

```python
from flask_smorest import Api

app.config.update(
    API_TITLE="CareerPilot API",
    API_VERSION="v1",
    OPENAPI_VERSION="3.0.3",
    OPENAPI_URL_PREFIX="/docs",
    OPENAPI_JSON_PATH="openapi.json",
    OPENAPI_SWAGGER_UI_PATH="/swagger-ui",
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
)
api = Api(app)
api.spec.components.security_scheme("BearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"})
```

Open `http://localhost:5091/docs/swagger-ui` to try endpoints in the browser.

### 4. Documenting endpoints with the schemas you already have

This is the payoff of lesson 03: the schema that validates the request also describes it in the docs, so the two can never disagree.

```python
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint("companies", __name__, url_prefix="/api/v1/companies", description="Companies you apply to")

@blp.route("")
class Companies(MethodView):
    @blp.arguments(CompanyQuerySchema, location="query")
    @blp.response(200, CompanySchema(many=True))
    def get(self, query):
        """List companies

        Sorted by name. Use `q` to search by name (case-insensitive).
        """
        return company_service().list(query)

    @blp.arguments(CompanyCreateSchema)
    @blp.response(201, CompanySchema)
    @blp.alt_response(409, schema=ErrorSchema, description="A company with this name already exists")
    @blp.doc(security=[{"BearerAuth": []}])
    def post(self, data):
        """Create a company"""
        return company_service().create(data)
```

- `@blp.arguments` **validates** input and **documents** it — one source of truth.
- `@blp.response` **serializes** output with the schema and documents it.
- The docstring's first line becomes the `summary`; the rest becomes the `description`.
- `@blp.alt_response` documents other outcomes (errors).

### 5. Descriptions and examples in schemas

```python
class CompanyCreateSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        metadata={"description": "Company name, unique (case-insensitive)", "example": "Kopi Data"},
    )
```

Good examples are the fastest way for a frontend developer to understand a field.

### 6. Errors in your own format

flask-smorest's default validation error looks like `{"code": 422, "errors": {"json": {...}}, "status": "..."}`. Register a handler to keep **your** envelope, and document an `ErrorSchema` for it:

```python
@app.errorhandler(422)
def validation_error(error):
    messages = getattr(error, "data", {}).get("messages", {})     # {"json": {"name": ["…"]}, "query": {...}}
    fields = {f"{location}.{name}": msgs[0] for location, errs in messages.items() for name, msgs in errs.items()}
    return {"error": {"code": "validation_failed", "message": "Some fields are invalid", "fields": fields}}, 422
```

### 7. Test the spec

A test that fails when the spec breaks turns documentation into something the pipeline protects, instead of something people remember to update.

```python
def test_openapi_spec(client):
    spec = client.get("/docs/openapi.json").get_json()
    post = spec["paths"]["/api/v1/companies"]["post"]
    assert {"201", "409", "422"} <= set(post["responses"])
    assert post["security"] == [{"BearerAuth": []}]
```

Also run a **spec linter** (e.g. Spectral, Redocly) in CI, and consider **contract tests** (e.g. Schemathesis generates requests from your spec and checks responses match).

### 8. What the spec unlocks

| Use | Tool examples |
|---|---|
| Interactive docs | Swagger UI, Redoc, Scalar |
| Typed client generation | `openapi-typescript` for your Next.js app (Module 4), openapi-generator |
| Mock server before the backend exists | Prism |
| Contract / fuzz testing | Schemathesis |
| Import into API clients | Postman, Bruno, Insomnia |
| AI tools | agents and LLM "tool" definitions can be generated from OpenAPI (Module 7) |

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Code-first generation | never drifts; low effort | spec quality depends on code annotations |
| Design-first | contract agreed before coding; parallel work | must keep code in sync (codegen/contract tests) |
| Hand-written markdown docs | flexible narrative | always drifts |
| Public Swagger UI in production | easy exploration | exposes attack surface — protect or disable for internal APIs |
| Rich examples | faster onboarding | must be kept realistic |

- ✅ Every HTTP API that has more than one consumer (including "future you" and your frontend).
- ✅ Add docstrings, examples, error responses and security to every endpoint.
- 🚫 Don't expose internal admin endpoints' docs publicly.
- 🚫 Don't document fields or errors that the code doesn't actually return.

## ⚠️ Common mistakes

- Only documenting the happy path.
- Documenting a schema that differs from what the endpoint returns (bypassing `@blp.response`).
- Missing security declarations → "Try it out" fails confusingly.
- Leaving default placeholder titles/versions.
- Exposing internal endpoints publicly through the docs.

:::revoshop
RevoShop already serves docs: `config/base.py` sets `OPENAPI_URL_PREFIX = '/docs'` and Swagger UI, and `create_app()` adds a `BearerAuth` security scheme with the description *"Paste the access_token returned by /api/v1/auth/login"*. Run the app and open `/docs/swagger-ui`: (1) Do **all** endpoints show their error responses (`404`, `409`, `422`), or only success? (2) Do protected endpoints show the lock icon? (3) Do schemas have field descriptions and examples? (4) Does the documented error format match what your `app/errors.py` actually returns? Pick the three weakest endpoints and improve their docs — then add a test that checks the spec.
:::

## 🏆 Best practices

- [ ] Generate the spec from the **same schemas** that validate and serialize (code-first) — or enforce design-first with contract tests.
- [ ] Every operation: **summary**, **description**, **tags**, request schema, success **and** error responses.
- [ ] Add **descriptions and examples** to schema fields.
- [ ] Declare **security schemes** and mark protected operations.
- [ ] Keep one **error schema** and document it on every endpoint that can fail.
- [ ] **Test the spec** in CI (structure tests, a linter, optionally contract tests).
- [ ] Version the API (`/api/v1`) and publish a changelog for breaking changes.
- [ ] Protect or disable Swagger UI in production for non-public APIs.
- [ ] Generate typed clients from the spec for your frontend.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer what an OpenAPI spec is and why generating docs from code is better than writing them in a Google Doc.

## 📐 Design it

For CareerPilot's `POST /api/v1/applications/{id}/status`, write the documentation you'd want: summary, description, tags, path parameter, request body (with example), all responses (with descriptions and which schema), and security. Then list what automated check would catch the docs drifting from the code.

:::quiz
Show a possible documentation plan

- **Summary:** Change an application's status
- **Description:** Moves the application through its pipeline. Allowed transitions: applied → interview/rejected/withdrawn; interview → interview/offer/rejected/withdrawn; offer → accepted/declined. Records a history entry.
- **Tags:** applications · **Security:** BearerAuth
- **Path param:** `id` (integer, the application id)
- **Body:** `StatusChangeSchema` — `status` (enum of allowed values, example `"interview"`), optional `note` (≤ 500 chars, example `"Technical round scheduled"`)
- **Responses:** `200` `ApplicationSchema` · `401` `ErrorSchema` (missing/expired token) · `404` `ErrorSchema` (not found or not yours) · `409` `ErrorSchema` (`invalid_transition`) · `422` `ErrorSchema` (`validation_failed`)

**Drift checks:** a pytest that loads `/docs/openapi.json` and asserts these responses and security; Schemathesis running against the spec in CI; the frontend's generated TypeScript types failing to compile when fields change.
:::

### 📝 Self-review checklist

- [ ] Error responses are documented, not only 200
- [ ] Business rules (allowed transitions) are in the description
- [ ] Request fields have examples
- [ ] There's an automated drift check

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w5/07-openapi-docs" ai="no-ai" title="A self-documenting companies API"}
Build a small companies API with **flask-smorest** (in memory, no database): documented query and body schemas with descriptions and examples, success and error responses, a Bearer security scheme on protected operations, tags, docstring summaries, and a custom `422` handler that keeps the handbook's error envelope. The tests read your `/docs/openapi.json` and check it matches what the endpoints really do.
:::

:::hints
- `api.spec.components.security_scheme("BearerAuth", {...})` right after creating `Api(app)`.
- `@blp.alt_response(404, schema=ErrorSchema, description="...")` for each error.
- `metadata={"description": "...", "example": ...}` on schema fields.
- The `422` handler receives an exception whose `.data["messages"]` holds `{location: {field: [messages]}}`.
:::

### 🏆 Stretch goal

Run [Schemathesis](https://schemathesis.readthedocs.io/) against your running app (`uvx schemathesis run http://localhost:5091/docs/openapi.json`) and fix anything it finds.

## ✅ Quick check

:::quiz
What's the main advantage of generating OpenAPI from code?

The documentation comes from the same schemas and decorators that validate and serialize real requests, so it can't silently drift from the implementation.
:::

:::quiz
Name three things an OpenAPI spec enables besides human-readable docs.

Typed client generation, mock servers, contract/fuzz testing, importing into API clients or gateways, and generating AI tool definitions.
:::


## 📚 Keep learning

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [flask-smorest documentation](https://flask-smorest.readthedocs.io/)
- [Schemathesis — property-based API testing](https://schemathesis.readthedocs.io/)
