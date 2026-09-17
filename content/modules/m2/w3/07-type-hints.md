---
title: "Type Hints & Static Type Checking"
summary: Describe what your functions accept and return, let mypy/pyright catch bugs before running, and use the typing tools modern frameworks rely on.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: core, ops: optional }
durationMinutes: 120
tags: [python, typing, mypy, pyright, bonus]
lastReviewed: 2026-09
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Annotating variables, functions, collections and optional values
- Union types (`X | None`), `Literal`, `TypedDict`, `Protocol`, `Callable`
- Generics basics: `list[T]`, `TypeVar` / the new `def first[T](...)` syntax
- Running a **static type checker** (mypy or pyright) locally and in CI
- Why FastAPI and Pydantic (Module 3) turn type hints into runtime validation

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Type hint** | A note saying what kind of value goes in and comes out | Petunjuk jenis data |
| **Static type checker** | A tool (mypy, pyright) that reads those notes and finds mismatches without running the code | Pemeriksa tipe tanpa menjalankan |
| **Dynamic typing** | Python only checks types while running | Pemeriksaan saat jalan |
| **`X \| None`** | "Either an X or nothing" — must be handled | Bisa X atau kosong |
| **`Literal`** | Only these exact values are allowed (`"applied"`, `"offer"`) | Hanya nilai tertentu |
| **`TypedDict`** | A dict whose keys and value types are known | Dict dengan bentuk pasti |
| **`Protocol`** | "Anything with these methods fits" | Cukup punya metode ini |
| **Generic (`list[T]`)** | A container described together with what it holds | Wadah beserta isinya |
| **Type alias** | A short name for a long type | Nama pendek untuk tipe |

## 🧠 The big idea

:term[Type hints]{bahasa="petunjuk tipe — anotasi yang menjelaskan jenis data yang diterima dan dikembalikan fungsi"} are **labels on the pipes** in a building: "hot water", "gas", "drain".

The water doesn't care — Python still runs without checking them — but the plumbers (your editor and the type checker) can see instantly when someone connects the gas pipe to the sink.

## ❓ Why it matters

Python checks types only while running, so a mistake like passing `None` where a string is expected shows up when that line finally runs — maybe in production, at 2 a.m. Type hints let tools catch a whole class of bugs **before** running, power your editor's autocomplete, and document what a function expects right where you read it.

Without them:

```python
def find_user(email):
    ...                       # returns a User — or None if not found

def greeting(email):
    user = find_user(email)
    return "Hi " + user.name   # 💥 AttributeError: 'NoneType' has no attribute 'name' — only for unknown emails
```

With them, the checker tells you immediately:

```python
def find_user(email: str) -> User | None: ...

def greeting(email: str) -> str:
    user = find_user(email)
    return "Hi " + user.name   # error: Item "None" of "User | None" has no attribute "name"
```

## 📖 Step by step

### 1. The basics

```python
count: int = 0
names: list[str] = []
prices: dict[str, int] = {}
point: tuple[float, float] = (-6.2, 106.8)
ids: set[int] = set()

def apply_discount(price: int, percent: int = 10) -> int:
    return price * (100 - percent) // 100

def log(message: str) -> None:     # returns nothing
    print(message)
```

Built-in generics (`list[str]`, `dict[str, int]`) work directly in modern Python — no `from typing import List` needed.

### 2. Optional values and unions

`User | None` is the type system saying "this box may be empty — open it carefully". That single hint prevents most `NoneType` crashes.

```python
def parse_salary(text: str) -> int | None:
    text = text.strip()
    return int(text) if text else None

salary = parse_salary(raw)
if salary is not None:        # "narrowing": after this check, the checker knows salary is int
    print(salary + 1)
```

`int | None` means "an int or None". Checkers force you to handle the `None` case — that's the point.

### 3. More precise types

```python
from typing import Literal, TypedDict, Protocol, Callable, Final

Status = Literal["applied", "interview", "offer", "rejected"]      # only these strings

class JobDict(TypedDict):          # a dict with known keys (e.g. JSON payloads)
    title: str
    salary_max: int | None

class Notifier(Protocol):          # any object with this method fits ("duck typing" for checkers)
    def send(self, recipient: str, message: str) -> None: ...

Handler = Callable[[dict], str]    # a function taking a dict, returning a str

MAX_RETRIES: Final = 3             # must not be reassigned
```

`Protocol` is how you type **dependency injection** without inheritance: `ReminderService(notifier: Notifier)` accepts any class with a matching `send`.

### 4. Generics

```python
def first[T](items: list[T]) -> T | None:        # Python 3.12 syntax
    return items[0] if items else None

first([1, 2, 3])        # checker knows: int | None
first(["a"])            # str | None
```

(Older equivalent: `T = TypeVar("T")` then `def first(items: list[T]) -> T | None`.)

### 5. Type aliases

```python
type UserId = int                               # Python 3.12
type SkillCounts = dict[str, int]

def top_skills(counts: SkillCounts, n: int) -> list[tuple[str, int]]: ...
```

### 6. Running a type checker

```bash
uv add --dev mypy          # or: pyright / basedpyright
uv run mypy src/           # check a folder
```

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true              # start strict on new projects; relax per module for legacy code
```

VS Code's Pylance (pyright) shows the same kind of errors as you type.

### 7. Hints become validation (preview)

In Module 3, FastAPI and Pydantic read these same labels and use them to check incoming requests at runtime — the pipe labels become an actual inspector at the door.

Type hints do **nothing at runtime** in plain Python:

```python
apply_discount("100", "abc")   # runs, then crashes inside — hints didn't stop it
```

Libraries like **Pydantic** and **FastAPI** read your hints and **validate** incoming data at runtime:

```python
class ApplicationIn(BaseModel):
    company_id: int
    status: Literal["applied", "interview"] = "applied"
# {"company_id": "abc"} → automatic 422 error with a clear message
```

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Type hints + checker | catch bugs early, autocomplete, self-documenting | extra syntax; occasional fights with dynamic code |
| No hints | quick for tiny scripts | bugs found at runtime; harder refactors |
| `strict` mode | maximum safety | noisy on legacy code |
| `Any` | escape hatch | turns checking off for that value |
| `TypedDict` | types for JSON-shaped dicts | no runtime validation |
| Pydantic models | runtime validation | dependency, some overhead |

- ✅ Type **all** function signatures in application code; run a checker in CI.
- ✅ `X | None` for anything that can be missing — and handle it.
- ✅ `Protocol` for injected dependencies; `Literal` for fixed string sets.
- 🚫 Don't sprinkle `Any` or `# type: ignore` to silence real problems.
- 🚫 Don't mistake type hints for input validation at API boundaries — validate at runtime too.

## ⚠️ Common mistakes

- Forgetting `| None` for functions that can return nothing.
- Using `list` without an item type (`list` instead of `list[Job]`).
- Believing hints validate data at runtime.
- `def f(items: list = [])` — still a mutable default, even with hints.
- Silencing errors with `Any` instead of fixing the design.

:::revoshop
Pick three functions in RevoShop's `app/services/`. Do they have type hints for all parameters and return values? Add hints to one service in a branch and run `uv run mypy app/services/<file>.py` (install mypy temporarily). What does it report? Look especially for places where a repository can return `None` (e.g. "product not found") and the service uses the result without checking.
:::

## 🏆 Best practices

- [ ] Annotate **every function signature** (parameters and return type), including `-> None`.
- [ ] Use modern syntax: `list[str]`, `X | None`, `type` aliases (3.12+).
- [ ] Run **mypy or pyright in CI**; use `strict` for new code.
- [ ] Narrow optional values with explicit checks (`if x is None: …`) instead of assuming.
- [ ] Prefer precise types (`Literal`, `TypedDict`, dataclasses, Protocols) over `dict`/`Any`.
- [ ] Keep `# type: ignore[code]` rare, specific, and commented with the reason.
- [ ] Validate external input at runtime (Pydantic/marshmallow); rely on types inside.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why labeling a function's inputs and outputs helps a team, even though Python ignores the labels when running.

## 📐 Design it

Write full type signatures (no bodies) for CareerPilot's application service:

- create an application (user id, company id, role, optional salary expectation) → the new application
- find by id for a user → the application or nothing
- change status → the updated application; status must be one of the allowed values
- list for a user with optional status filter and pagination → a page object with items and total
- the service receives a repository and a clock (injected)

:::quiz
Show possible signatures

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol, Callable

type Status = Literal["wishlist", "applied", "interview", "offer", "rejected", "withdrawn"]

@dataclass(frozen=True, slots=True)
class Page[T]:
    items: list[T]
    total: int

class ApplicationRepository(Protocol):
    def add(self, application: "Application") -> "Application": ...
    def get_for_user(self, application_id: int, user_id: int) -> "Application | None": ...
    def list_for_user(self, user_id: int, status: Status | None, limit: int, offset: int) -> Page["Application"]: ...

class ApplicationService:
    def __init__(self, repository: ApplicationRepository, clock: Callable[[], datetime]) -> None: ...
    def create(self, user_id: int, company_id: int, role_title: str, salary_expectation: int | None = None) -> "Application": ...
    def get(self, user_id: int, application_id: int) -> "Application | None": ...
    def change_status(self, user_id: int, application_id: int, status: Status) -> "Application": ...
    def list(self, user_id: int, *, status: Status | None = None, page: int = 1, per_page: int = 20) -> Page["Application"]: ...
```
:::

### 📝 Self-review checklist

- [ ] "Might not exist" returns are `X | None`
- [ ] Statuses use `Literal` (or an Enum)
- [ ] Dependencies are typed with `Protocol`/`Callable`
- [ ] Options are keyword-only

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w3/07-type-hints" ai="no-ai" title="Type it, then let mypy judge"}
`service.py` works at runtime but has **no** type hints and two hidden `None` bugs. Add complete, precise hints (`Literal`, `TypedDict`, `Protocol`, `X | None`, generics) and fix the bugs the checker reveals. The tests run your code **and** run `mypy --strict` on your file.
:::

:::hints
- Run `uv run mypy --strict m2/w3/07-type-hints/service.py` from `exercises/` and read the first error.
- `dict.get()` returns `X | None` — mypy will make you handle it.
- A `Protocol` for the repository lets the test's fake repository type-check.
:::

## ✅ Quick check

:::quiz
Do type hints prevent `apply_discount("100")` from running?

No. Python ignores hints at runtime. A type checker reports the mistake before running; runtime validation libraries (Pydantic) can enforce types on incoming data.
:::

:::quiz
What does `Protocol` let you do?

Describe the methods an object must have, so any class with matching methods is accepted by the type checker — without inheriting from a base class.
:::


## 📚 Keep learning

- [Python docs: typing](https://docs.python.org/3/library/typing.html)
- [mypy: Getting started](https://mypy.readthedocs.io/en/stable/getting_started.html)
- [Pydantic: Why use Pydantic](https://docs.pydantic.dev/latest/why/)
