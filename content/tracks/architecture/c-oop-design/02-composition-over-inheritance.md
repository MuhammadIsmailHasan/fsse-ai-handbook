---
title: "Composition over Inheritance"
summary: Build behavior by combining small objects instead of deep class trees — when inheritance fits, why it breaks, and how composition keeps Python code flexible.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: recommended, ops: optional }
durationMinutes: 120
tags: [architecture, oop, composition, inheritance, mixins]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **Is-a** (inheritance) vs **has-a** (composition)
- The problems of deep hierarchies: class explosion, fragile base classes, tight coupling
- Composition patterns in Python: delegation, strategy objects, collections of capabilities
- When inheritance is the right tool (and how to use it safely)
- Mixins and multiple inheritance — with care

## 🧠 The big idea

Inheritance is like **genetics**: a child inherits everything from its parents, forever, and can't pick and choose. Composition is like **LEGO**: you build a thing from bricks, and you can swap a wheel for a propeller at any time.

When the combinations of features multiply (role × plan × region…), genetics produces a family tree you can't manage. LEGO just adds a brick.

## ❓ Why does this exist?

Early OOP teaching emphasized inheritance for reuse. Decades of experience (the *Design Patterns* book, 1994, already said "favor object composition over class inheritance") showed that inheritance couples subclasses tightly to parents' internals, while most real-world variation is better modeled as **parts you can combine and replace**.

## 💥 What happens if we DON'T?

```text
User
├── JobSeeker
│   └── ProJobSeeker
├── Recruiter
│   └── ProRecruiter
└── RecruiterWhoIsAlsoJobSeeker (multiple inheritance 😬)
        └── ProRecruiterWhoIsAlsoJobSeeker ...
```

- Adding an "Enterprise" plan doubles the classes.
- Upgrading a user to Pro means creating a **different object** and copying data.
- A change in `User.can()` silently changes behavior in five subclasses (**fragile base class**).
- Multiple inheritance makes method resolution order a puzzle.

## 📖 How it works, step by step

### 1. Is-a vs has-a

Ask: **is this a permanent, true "is-a" that shares the full contract?** Or does the object **have** a capability that can vary or change?

| Relationship | Better model |
|---|---|
| `Account` **has** roles, **has** a plan | composition |
| `Notifier` **has** a retry policy | composition |
| `ValidationError` **is a** `ValueError` | inheritance ✅ |
| `PostgresRepository` **is a** implementation of `Repository` | protocol (structural) or ABC |

### 2. Composition by collecting capabilities

```python
@dataclass(frozen=True)
class Role:
    name: str
    permissions: frozenset[str]

class Account:
    def __init__(self, email, roles=(), plan=FREE):
        self.roles = set(roles)
        self.plan = plan

    def can(self, permission):
        return any(permission in role.permissions for role in self.roles)
```

New role combinations are **data**. Changing a plan is `account.plan = PRO`. No new classes.

### 3. Composition by delegation

```python
class ReportService:
    def __init__(self, repository, renderer, clock):
        self._repository = repository      # has-a
        self._renderer = renderer          # has-a
        self._clock = clock

    def monthly(self, user_id):
        apps = self._repository.list_for_user(user_id)
        return self._renderer.render(apps, generated_at=self._clock())
```

Swap the renderer (PDF → HTML) or the repository (Postgres → fake) without subclassing `ReportService`.

### 4. Why inheritance couples so tightly

```python
class BaseImporter:
    def run(self):
        for row in self.rows():
            self.save(row)

class CsvImporter(BaseImporter):
    def save(self, row):
        self.count += 1          # relies on base class calling save once per row
        super().save(row)
```

If the base class later batches saves (`save_many`), `CsvImporter` silently breaks: subclasses depend on **how** the parent works, not just **what** it promises. That's the fragile base class problem.

### 5. When inheritance is fine

- **Exception hierarchies**: `class InvalidTransition(DomainError)` — callers catch families of errors.
- **Framework extension points** designed for subclassing: `flask.views.MethodView`, Django class-based views, `unittest.TestCase`, SQLAlchemy `DeclarativeBase`.
- **Template Method** with a small, stable base (Stage D).
- Shallow (1 level), with the full contract honored (Liskov).

### 6. Mixins — small, focused inheritance

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Application(TimestampMixin, db.Model): ...
```

Useful for **adding** independent, stateless-ish features. Keep mixins tiny, don't let them depend on each other, and avoid diamond hierarchies.

### 7. Protocols replace most "interface inheritance" in Python

```python
class Renderer(Protocol):
    def render(self, applications, generated_at) -> str: ...
```

Any class with `render` works — no base class to inherit from, so nothing to become fragile.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Inheritance | little code, natural for true is-a and frameworks | tight coupling, class explosion, can't change at runtime |
| Composition | flexible, runtime changes, easy testing | more wiring, a few more objects to read |
| Mixins | reuse small behaviors | MRO complexity if overused |
| Protocols | no coupling to a base class | no shared implementation (use helper functions/composition for that) |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Composition: variations that combine (roles × plans), behaviors that change at runtime, anything you want to fake in tests.
- ✅ Inheritance: exceptions, framework hooks, genuinely stable is-a relationships.
- 🚫 Inheritance just to reuse a couple of methods — extract a function or a helper object.
- 🚫 Deep hierarchies (more than 2 levels) in application code.

## 🏆 Best practices

- [ ] Default to composition; justify inheritance with a real is-a and a stable contract.
- [ ] Keep hierarchies **shallow**; prefer protocols for polymorphism.
- [ ] Model roles, plans, permissions and settings as **data** (frozen dataclasses, enums), not subclasses.
- [ ] Inject collaborators through the constructor; don't create them inside methods.
- [ ] If you subclass framework classes, override only the documented hooks.
- [ ] Use mixins sparingly, for independent features, without state conflicts.

## 🏭 How it's used in industry

- Game engines use Entity–Component–System (entities **have** components) instead of `FlyingShootingEnemy` class trees.
- React replaced class component inheritance with composition of components and hooks (Module 4).
- Authorization libraries model roles and permissions as data (RBAC tables, policy documents like AWS IAM).

## ⚠️ Common mistakes

- `class Admin(User)` for a role that can change.
- Overriding a parent method to do nothing or raise — a sign the subclass isn't really a subtype.
- Calling `super()` in fragile orders across multiple mixins.
- Composition everywhere for trivial code, creating needless indirection.

:::revoshop
RevoShop has buyers, sellers and admins. (1) Look at `app/models/users.py`: are roles a column (data) or classes? (2) What would it take for one person to be both a buyer and a seller? (3) Search `app/services/` for `if role ==` checks — how many places would change if you added a "support" role? Sketch a `Role` + permissions model and a single `can(user, permission)` function.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a junior developer why `class ProRecruiter(Recruiter)` becomes a problem once the product adds an "Enterprise" plan and lets recruiters also look for jobs. Use the LEGO vs genetics analogy.

## 📐 Design it

CareerPilot's job importers pull listings from different boards. Each board needs a different **fetching** method (REST API, RSS, CSV upload), a different **parser**, optional **rate limiting**, and optional **deduplication**. Design this with composition: which objects exist, what the importer holds, and how you'd create "RSS + dedupe, no rate limit" and "API + rate limit + dedupe" without new subclasses.

:::quiz
Show a possible design

```python
class Fetcher(Protocol):   def fetch(self) -> Iterable[bytes]: ...
class Parser(Protocol):    def parse(self, raw: bytes) -> list[JobPosting]: ...
class Filter(Protocol):    def apply(self, jobs: list[JobPosting]) -> list[JobPosting]: ...

class ApiFetcher: ...          # uses an injected HTTP client
class RssFetcher: ...
class RateLimitedFetcher:      # wraps any Fetcher (composition/decorator)
    def __init__(self, inner: Fetcher, limiter): ...
class DedupeFilter: ...        # uses a seen-key store

class JobImporter:
    def __init__(self, fetcher: Fetcher, parser: Parser, filters: list[Filter], repository):
        ...
    def run(self) -> ImportReport:
        jobs = [job for raw in self.fetcher.fetch() for job in self.parser.parse(raw)]
        for f in self.filters:
            jobs = f.apply(jobs)
        self.repository.add_many(jobs)
```

Configurations are just different assemblies:
- `JobImporter(RssFetcher(url), RssParser(), [DedupeFilter(store)], repo)`
- `JobImporter(RateLimitedFetcher(ApiFetcher(client), limiter), KalibrrJsonParser(), [DedupeFilter(store)], repo)`

A new board = a new fetcher/parser pair, reused filters. Optional features = present or absent objects, not subclass combinations. (Stage D names the patterns: Strategy, Decorator, Pipeline.)
:::

### 📝 Self-review checklist

- [ ] Variation points are separate objects
- [ ] Optional behaviors don't require new subclasses
- [ ] Each part can be faked in tests

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/c-oop-design/02-composition-accounts" ai="no-ai" title="Replace a class explosion with roles and plans"}
Turn a `JobSeeker`/`Recruiter`/`ProRecruiter` hierarchy into an `Account` that **has** roles and a plan. Roles and plans change at runtime on the same object, permissions support wildcards, and a test checks no class inherits from another.
:::

:::hints
- Roles and plans are frozen dataclasses — values, not behavior-heavy classes.
- `can()`: build the set `{permission, "*", f"{resource}:*"}` and check it against each role's permissions.
- `limit()`: `self.plan.limits.get(name, 0)`.
:::

## ✅ Quick check

:::quiz
What is the "fragile base class" problem?

Subclasses depend on implementation details of their parent, so a seemingly safe change in the base class breaks subclasses in unexpected ways.
:::

:::quiz
Give one good use of inheritance in Python.

Exception hierarchies (e.g. `class InvalidTransition(DomainError)`), or documented framework extension points like `MethodView`.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Inheritance | Pewarisan |
| Composition | Komposisi — menyusun objek dari bagian-bagian |
| Delegation | Delegasi — meneruskan pekerjaan ke objek lain |
| Fragile base class | Kelas induk yang rapuh |
| Mixin | Kelas kecil untuk menambah fitur |
| Method resolution order (MRO) | Urutan pencarian metode |

## 📚 Keep learning

- [Python docs: dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Real Python: Inheritance and Composition — A Python OOP Guide](https://realpython.com/inheritance-composition-python/)

## 📣 Stage C done — share it

:::linkedin{type="concept"}
💡 "Favor composition over inheritance" finally clicked for me.

I modeled users as JobSeeker → ProJobSeeker → RecruiterWhoIsAlsoJobSeeker… and every new plan doubled the classes. Upgrading a user meant replacing the object.

The fix: an Account that *has* roles and *has* a plan. New combinations are data, not classes — and a plan change is one assignment.

Rule of thumb I'm using now: inheritance for true, stable "is-a" (like exception types); composition for everything that varies or changes at runtime.

Where did deep inheritance bite you? 👇

#SoftwareDesign #OOP #Python #LearningInPublic
:::
