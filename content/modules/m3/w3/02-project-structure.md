---
title: "Project Structure for Real Apps"
summary: Grow a FastAPI app past one file — routers with APIRouter, schemas vs models, a services layer, settings from the environment, and the import rules that stop circular imports.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 120
tags: [fastapi, project-structure, apirouter, settings, layered-architecture]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Split a FastAPI app into **routers**, **schemas**, **services**, **repositories** and **models**
- Use **`APIRouter`** and `include_router` to group endpoints
- Tell **schemas** (API shapes) from **models** (database tables)
- Load **settings** from the environment in one place
- Follow **import rules** so you never get a circular import

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Router** | A group of related endpoints in its own file | Kelompok endpoint |
| **Schema** | The shape of data going in or out of the API | Bentuk data API |
| **Model** | A class that maps to a database table | Kelas tabel database |
| **Service** | Business rules, with no HTTP inside | Aturan bisnis |
| **Repository** | The only code that talks to the database | Kode akses database |
| **Settings** | Config read from environment variables | Konfigurasi dari environment |
| **Circular import** | Module A needs B and B needs A, so Python fails | Impor melingkar |

## 🧠 The big idea

A growing app is like a **restaurant kitchen**. The waiter (router) takes the order and brings the plate. The chef (service) decides how to cook. The pantry clerk (repository) is the only one who opens the storeroom. Everyone has one job and talks only to the next person in line. The waiter never walks into the storeroom, and the storeroom never shouts at the customers.

## ❓ Why it matters

One `main.py` works for a demo. At 500 lines you scroll to find anything, two people edit the same file and collide, and you cannot test business rules without HTTP. Putting each job in its own place means a change touches one file, each part has its own tests, and a new teammate knows where to look. You saw the layers in RevoShop (Flask). FastAPI uses the same idea with its own tools: `APIRouter` instead of Blueprints, and Pydantic schemas next to SQLAlchemy models.

## 📖 Step by step

### 1. The folder layout

```text
app/
├── main.py            # creates the app, includes the routers
├── core/
│   ├── config.py      # settings from environment variables
│   └── deps.py        # shared dependencies (get_db, get_current_user)
├── routers/           # HTTP only: parse request, call a service, return
│   └── applications.py
├── schemas/           # Pydantic shapes for requests and responses
│   └── applications.py
├── services/          # business rules
│   └── applications.py
├── repositories/      # database queries
│   └── applications.py
├── models/            # SQLAlchemy tables
│   └── application.py
tests/
```

You do not need all of it on day one. Start with `main.py`, add a router when a second topic appears, add a service when a router gets rules in it.

### 2. A router with `APIRouter`

A router is a mini-app. You write endpoints on it, then plug it into the main app.

```python
# app/routers/applications.py
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.applications import ApplicationIn, ApplicationOut
from app.services import applications as service

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(body: ApplicationIn, user=Depends(get_current_user)):
    return service.create(user.id, body)
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import applications

app = FastAPI(title="CareerPilot")
app.include_router(applications.router)
```

`prefix` and `tags` are set once. The `tags` group the endpoints in the automatic docs. The route function stays **thin**: read the request, call the service, return the result.

### 3. Schemas are not models

They look alike, but they have different jobs.

| | Schema (Pydantic) | Model (SQLAlchemy) |
|---|---|---|
| Describes | what the API accepts and returns | a table in the database |
| Lives in | `schemas/` | `models/` |
| Example field | `ApplicationIn` has no `id` | `Application` has `id`, `user_id`, `created_at` |
| Danger if mixed | the API leaks internal columns | the database is shaped by the API |

Keep them apart. Then you can add a database column without changing the API, and you never return a `password_hash` by accident.

### 4. Services and repositories

The **service** holds the rules ("a user cannot save the same job twice"). The **repository** holds the queries. The service never builds SQL, and the repository never decides rules.

```python
# app/services/applications.py
def create(user_id: int, body: ApplicationIn):
    if repo.exists(user_id, body.company, body.title):
        raise DuplicateApplication()
    return repo.add(user_id, body)
```

Because the service does not know about HTTP, you can test it with plain Python, and a background job can reuse it.

### 5. Settings in one place

Read environment variables **once**, validate them, and import the result. Do not call `os.getenv` all over the code.

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    access_token_minutes: int = 15

settings = Settings()   # fails at startup if a value is missing
```

A missing `DATABASE_URL` stops the app at startup with a clear error, instead of failing at the first request in production. This is the "config from the environment" rule from the 12-factor approach.

### 6. Import rules prevent circular imports

Data flows one way: `routers → services → repositories → models`. Schemas, models and `core` import nothing from the layers above them. If a service imports a router, and a router imports that service, Python raises an error at startup.

When you feel the urge to import "upward", move the shared piece **down** into a lower layer, or pass it in as a function argument. A small script that checks the rules in CI (the exercise below) keeps the structure honest as the team grows.

### When to use what

| Situation | Do this |
|---|---|
| A new topic (users, jobs, applications) | a new router file |
| A route function has an `if` about business rules | move the rule into a service |
| The same query appears twice | put it in a repository function |
| A value comes from the environment | add it to `Settings` |
| Two modules need each other | move the shared code down a layer |
| A tiny app with 3 endpoints | one file is fine — do not over-build |

## ⚠️ Common mistakes

- Putting SQL or business rules inside route functions.
- Returning the SQLAlchemy model directly, so internal columns reach the client.
- Reading `os.environ` in many files instead of one `Settings` class.
- A "utils.py" that everything imports and that imports everything.
- Splitting into ten folders for a three-endpoint app.

:::revoshop
Look at how RevoShop is laid out (blueprints, schemas, services, repositories). (1) Which folder in FastAPI would each RevoShop blueprint become? (2) Find one route that holds a business rule — which service function would you extract? (3) Where does RevoShop read its environment variables, and is it in one place?
:::

## 🏆 Best practices

- [ ] One router file per topic, with `prefix` and `tags` set once.
- [ ] Keep route functions thin: parse, call a service, return.
- [ ] Keep Pydantic schemas and SQLAlchemy models separate.
- [ ] Load settings once with `pydantic-settings` and fail fast at startup.
- [ ] Imports go one way: routers → services → repositories → models.
- [ ] Add structure when it hurts, not before.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Use the restaurant-kitchen analogy to explain routers, services and repositories. Then say why a router should never talk to the database directly.

## 📐 Design it

Lay out the folders and files for CareerPilot's AI service: endpoints for `/applications`, `/jobs` and `/ai/cover-letter`. Say what goes in each layer, where the settings live, and which import you would forbid.

:::quiz
Show a possible design

- **`routers/`**: `applications.py`, `jobs.py`, `ai.py`, each with its own `prefix` and `tags`.
- **`schemas/`**: `ApplicationIn/Out`, `JobOut`, `CoverLetterRequest/Response`.
- **`services/`**: `applications.py` (duplicate rule, ownership), `cover_letters.py` (builds the prompt, calls the AI client).
- **`repositories/`**: `applications.py`, `jobs.py` — all queries.
- **`models/`**: `Application`, `Job`.
- **`core/`**: `config.py` (`Settings`: database URL, JWT secret, AI API key), `deps.py` (`get_db`, `get_current_user`).
- **Forbidden:** a service importing a router, or a router importing a repository. A CI check enforces it.
- **The AI client** sits behind a small class in `services/`, so tests can replace it with a fake.

**Rule shown:** one job per layer, one direction of imports, settings in one place.
:::

### 📝 Self-review checklist

- [ ] Each folder has one clear job
- [ ] Routes are thin; rules live in services
- [ ] Schemas and models are separate
- [ ] Settings are loaded once and validated at startup
- [ ] No imports go upward

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w3/02-layout" ai="no-ai" title="Check a project layout"}
Write the small checker a team could run in CI. In `layout_rules.py`, implement `layer_of`, `find_violations` (imports that break the layer rules) and `find_cycle` (one circular import path, or `None`). The tests cover a clean layout, router→repository, service→router, third-party imports, sorted output, and cycles with a tail.
:::

:::hints
- `layer_of("app.routers.users")` is the second part of `module.split(".")`.
- For each importer, skip imports that do not start with `app.`. Same layer and `core` are always fine; `app.main` may import anything.
- Compare with `ALLOWED[src]`; return `sorted(found)` so the output is stable.
- For cycles use a depth-first walk with a `visiting` list. If you reach a node already in `visiting`, slice from its position and add the node again at the end.
- A "tail" node like `x → a` is not part of the loop: slice from where the loop starts.
:::

## ✅ Quick check

:::quiz
Why keep Pydantic schemas and SQLAlchemy models separate?

They have different jobs. A schema is the contract with API clients; a model is the shape of a database table. If they are the same class, adding a column changes your API, and internal fields like `password_hash` can leak in a response. Separate classes let each change on its own.
:::

:::quiz
What is a circular import, and how do you fix one?

Module A imports B while B imports A, so Python cannot finish loading either one. Fix it by making imports flow one way (routers → services → repositories → models) and moving shared code down into a lower layer, or passing the needed piece in as an argument.
:::

## 📚 Keep learning

- [FastAPI: Bigger Applications — Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [pydantic-settings: Settings management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [The Twelve-Factor App: Config](https://12factor.net/config)
