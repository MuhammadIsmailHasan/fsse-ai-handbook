---
title: "Routing, Path, Query & Body"
summary: How FastAPI reads a request — path parameters from the URL, query parameters from the string after ?, and a typed Pydantic body from JSON, each validated automatically so your handler receives clean, typed values.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 100
tags: [fastapi, routing, path-params, query-params, request-body]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Declaring routes with HTTP methods (`@app.get`, `@app.post`, …)
- **Path parameters** — values inside the URL path
- **Query parameters** — values after `?`, with defaults and optionals
- **Request bodies** — typed JSON via a Pydantic model
- How FastAPI decides which is which, and validates each

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Route** | A URL + method mapped to a function | URL + method ke fungsi |
| **Path param** | A value inside the URL path (`/items/42`) | Nilai di dalam path |
| **Query param** | A value after `?` (`?q=phone&page=2`) | Nilai setelah `?` |
| **Request body** | JSON data sent with the request | Data JSON yang dikirim |
| **Default** | A value used when a param is omitted | Nilai bawaan |
| **Optional** | A param that may be absent (`| None`) | Boleh tidak ada |

## 🧠 The big idea

A request is like **ordering at a counter**. The **path** is *which* dish is on the menu board (`/coffee/latte`). The **query** is your *tweaks* (`?size=large&sugar=0`). The **body** is a *written order form* for something detailed (a whole custom cake). FastAPI reads all three from the right place and checks each is filled in correctly before the kitchen starts.

## ❓ Why it matters

Every endpoint reads inputs from somewhere: the URL, the query string, or the body. Mixing these up — or forgetting to validate them — is a classic source of bugs and `500` errors. FastAPI ties each input to a typed function argument and validates it, so your handler always receives clean, correctly-typed values. Knowing which input goes where is core REST design (from Module 2), now enforced by types.

## 📖 Step by step

### 1. Routes and methods

```python
@app.get("/items")          # list
@app.get("/items/{id}")     # read one
@app.post("/items")         # create
@app.put("/items/{id}")     # replace
@app.delete("/items/{id}")  # delete
```

Same REST methods you used in Flask — FastAPI just binds them to typed functions.

### 2. Path parameters

A `{name}` in the path becomes a typed argument:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):        # "/items/42" → item_id = 42 (int)
    return {"item_id": item_id}
```

`item_id: int` means `/items/abc` is rejected with `422` automatically — the value is validated and converted before your code runs.

### 3. Query parameters

Function arguments **not** in the path come from the query string:

```python
@app.get("/items")
def list_items(q: str | None = None, page: int = 1, limit: int = 20):
    # GET /items?q=phone&page=2  →  q="phone", page=2, limit=20 (default)
    ...
```

- A **default** (`page: int = 1`) makes the param optional with that value.
- `str | None = None` makes it truly optional (may be absent).
- Types are validated: `?page=abc` → `422`.

### 4. Request body (Pydantic)

For create/update, take a Pydantic model — FastAPI reads and validates the JSON body:

```python
class ItemIn(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: ItemIn):      # JSON body → validated ItemIn
    return {"name": item.name, "price": item.price}
```

### 5. Combining all three

```python
@app.put("/users/{user_id}/items/{item_id}")
def update(user_id: int, item_id: int, item: ItemIn, notify: bool = False):
    # user_id, item_id ← path ; item ← body ; notify ← query (?notify=true)
    ...
```

FastAPI's rule: **in the path → path param; a Pydantic model → body; anything else → query param.** Each is validated by its type.

### Choosing where an input belongs

| Input | Put it in |
|---|---|
| Which resource (an id) | **path** (`/items/{id}`) |
| Filtering / paging / options | **query** (`?q=&page=`) |
| The data being created/updated | **body** (Pydantic model) |
| A secret/token | header (not path/query) |

- ✅ Identify resources with path params; filter/page with query params.
- ✅ Send create/update data as a typed body, never in the query string.
- 🚫 Don't put large or sensitive data in the URL (it's logged and cached).

## ⚠️ Common mistakes

- Passing create data in the query string instead of a JSON body.
- Forgetting a default, making a query param unexpectedly required.
- Putting an id in the body when it belongs in the path.
- Using `POST` to fetch data that a `GET` with query params should return.
- Sending secrets in the URL, where they leak into logs and history.

:::revoshop
Map RevoShop's endpoints to FastAPI param types. (1) "Get product 42" → path param; write the signature. (2) "Search products, page 2, category=books" → query params with defaults; write it. (3) "Create an order" → a Pydantic body; which fields, and why must they be in the body not the query?
:::

## 🏆 Best practices

- [ ] Use path params for resource identity, query params for filtering/paging/options.
- [ ] Give optional query params sensible defaults; use `| None` for truly optional.
- [ ] Model create/update data as a typed Pydantic body.
- [ ] Keep secrets and large payloads out of the URL.
- [ ] Follow Module 2 REST conventions — methods and status codes are unchanged.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain path vs query vs body with the ordering-at-a-counter analogy (dish on the board, tweaks, written form). Then state FastAPI's rule for deciding which argument is which.

## 📐 Design it

Design CareerPilot's application endpoints: (a) get one application by id, (b) list a user's applications filtered by status with paging, (c) create an application. For each, decide path/query/body and write the FastAPI signature.

:::quiz
Show a possible design

```python
# (a) read one — id in the path
@app.get("/applications/{application_id}")
def get_application(application_id: int): ...

# (b) list with filter + paging — query params with defaults
@app.get("/users/{user_id}/applications")
def list_applications(user_id: int, status: str | None = None, page: int = 1, limit: int = 20): ...

# (c) create — typed body
class ApplicationIn(BaseModel):
    company: str
    role: str
    status: str = "saved"

@app.post("/users/{user_id}/applications")
def create_application(user_id: int, body: ApplicationIn): ...
```

- `application_id`, `user_id` identify resources → **path**.
- `status`, `page`, `limit` filter/paginate → **query** with defaults.
- The new application's data → **body** (a Pydantic model), because it's structured data being created, not a filter.

**Rule shown:** ids in the path, filters/paging in the query, created/updated data in a typed body — each validated by its type.
:::

### 📝 Self-review checklist

- [ ] Resource ids in the path
- [ ] Filters/paging in query params with defaults
- [ ] Create/update data in a typed body
- [ ] No secrets or bulk data in the URL

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w1/03-params" ai="no-ai" title="Path, query, and body in one API"}
Build a small FastAPI app with three endpoints: read one item by path id, list items with query filter + paging (defaults), and create an item from a Pydantic body. The tests check correct routing, defaults, `422` on a bad path type, and body validation.
:::

:::hints
- `@app.get("/items/{item_id}")` with `item_id: int`; return `{"item_id": item_id}`.
- `@app.get("/items")` with `q: str | None = None, page: int = 1` — return the received values so tests can check defaults.
- `@app.post("/items")` with `body: ItemIn` (a Pydantic model `name: str, price: float`).
- Requesting `/items/abc` should return `422` automatically.
:::

## ✅ Quick check

:::quiz
FastAPI sees a function argument that is not in the path and is not a Pydantic model. Where does it get its value?

From the **query string** — it becomes a query parameter (e.g. `?page=2`). FastAPI's rule: names in the path are path params, a Pydantic model is the request body, and everything else is a query parameter, each validated by its type.
:::

:::quiz
Why should the data for creating a resource go in the request body, not the query string?

Because it's structured, potentially large or sensitive data, and URLs are logged, cached, and length-limited. A typed JSON body keeps it validated by a Pydantic model and out of logs, while query params are meant for filters, paging, and small options.
:::

## 📚 Keep learning

- [FastAPI: path parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI: query parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [FastAPI: request body](https://fastapi.tiangolo.com/tutorial/body/)
