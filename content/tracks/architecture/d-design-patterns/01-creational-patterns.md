---
title: "Creational Patterns: Factory, Builder, Singleton"
summary: Control how objects get created — factories and registries for choosing implementations, builders for complex valid objects, and why Singleton is usually a trap (and what to do instead).
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: optional }
durationMinutes: 150
tags: [architecture, design-patterns, factory, builder, singleton]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What :term[design patterns]{bahasa="pola desain — solusi umum yang sudah terbukti untuk masalah desain yang berulang"} are — and aren't
- **Factory** (simple factory, factory method, registry) for choosing implementations
- **Builder** for objects with many optional parts and validation rules
- **Singleton**: why global instances hurt testing, and Pythonic alternatives
- How Python features (first-class classes, decorators, modules, `functools.cache`) simplify these patterns

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Design pattern** | A named, proven solution to a problem that keeps coming back | Pola solusi yang sudah terbukti |
| **Factory** | One place that decides which class to create | Pusat pembuat objek |
| **Registry** | A table mapping a name to the class that handles it | Daftar nama ke kelas |
| **Builder** | Building a complex object step by step, validated at the end | Pembangun bertahap |
| **Singleton** | Exactly one shared instance for the whole program | Satu instance bersama |
| **Global state** | Shared data anything can reach — hard to test | Data global |
| **`functools.cache`** | Python's simple way to reuse one created object | Cara menyimpan hasil pembuatan |

## 🧠 The big idea

Patterns are **names for solutions you'll keep reinventing**. Saying "use a factory with a registry" in a code review communicates a whole design in five words — like a doctor saying "fracture" instead of describing the X-ray.

Creational patterns answer one question: **who decides which object gets created, and how?**

## ❓ Why it matters

Creating an object looks trivial — `CsvExporter()` — until:

- the class to create depends on **configuration or user input** (`format=xlsx`),
- an object has **ten optional settings** and must always end up **valid**,
- everybody needs **the same shared thing** (settings, a database engine, an HTTP client).

Then the creation code spreads: `if format == "csv" … elif …` in six files, half-built objects, and a shared instance nobody can replace in tests.

Patterns are also **names for solutions you'll keep reinventing**: saying "use a factory with a registry" in a review communicates a whole design in five words, like a doctor saying "fracture" instead of describing the X-ray.

## 📖 Step by step

### 1. Factory: centralize "which class?"

```python
def create_exporter(name: str, **options):
    if name == "csv":
        return CsvExporter(**options)
    if name == "json":
        return JsonExporter(**options)
    raise ValueError(f"unknown exporter {name!r}")
```

One place to change; callers depend on "an exporter", not on concrete classes (SOLID's D).

### 2. Registry: a factory that's open for extension

A registry is the phone directory version of a factory: adding a new exporter means adding one line to the directory, not editing an `if` chain everyone else is also editing.

In Python, classes are objects — store them in a dict and register with a decorator:

```python
EXPORTERS: dict[str, type] = {}

def register_exporter(name):
    def decorator(cls):
        if name in EXPORTERS:
            raise ValueError(f"exporter {name!r} is already registered")
        EXPORTERS[name] = cls
        return cls
    return decorator

@register_exporter("csv")
class CsvLinesExporter: ...

def create_exporter(name, **options):
    try:
        return EXPORTERS[name](**options)
    except KeyError:
        raise ValueError(f"unknown exporter {name!r} (available: {', '.join(sorted(EXPORTERS))})") from None
```

New formats register themselves; the factory never changes. Flask's `app.route`, pytest plugins and Django's admin use the same idea.

:::note[Factory Method vs Abstract Factory]
In classic OOP books, **Factory Method** is a method subclasses override to choose what to create, and **Abstract Factory** creates *families* of related objects (e.g. `AwsFactory` → S3 storage + SQS queue; `LocalFactory` → folder storage + in-memory queue). In Python, a function or a dict of callables usually does the job.
:::

### 3. Builder: step-by-step construction with validation at the end

```python
posting = (
    JobPostingBuilder()
    .titled("Backend Engineer")
    .at("Kopi Data")
    .in_city("Jakarta")
    .salary(9_000_000, 14_000_000)
    .requires("Python", "SQL")
    .build()                       # validates everything, returns a frozen object
)
```

- Readable: each call names what it sets.
- Collects parts gradually (skills added from several places, normalized once).
- `build()` enforces **cross-field rules** (city *or* remote; min ≤ max) and returns an **immutable** result.

**Pythonic alternative**: for simple cases, keyword arguments + a dataclass with `__post_init__` validation is enough. Reach for a builder when construction is multi-step, conditional, or reused (test data builders, query builders like SQLAlchemy's `select().where().order_by()`).

### 4. Singleton: one instance — and the trap

The trap is that a single global instance is shared by your tests too, so one test's changes leak into the next. In Python you rarely need the pattern: a module-level object or a cached factory function does the job and stays replaceable.

The classic Singleton guarantees a class has one instance with global access:

```python
class Settings:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

Why it's usually a trap:
- **Hidden global state**: any code can read or change it; dependencies are invisible in function signatures.
- **Hard to test**: tests share state and leak into each other; you can't easily use different settings per test.
- **Import-time side effects**: creating it at import reads env vars/connects to services before the app is configured.

Better options in Python:

| Need | Do this |
|---|---|
| One shared, lazily created object | a function with `@functools.cache` (resettable via `.cache_clear()`) |
| Config for the app | build it in `create_app()` and pass it / store on `app.config` |
| One DB engine / HTTP client per process | create in the app factory or composition root, inject where needed |
| "Module-level singleton" | a module is already a singleton — but keep it free of side effects at import |

```python
@cache
def get_settings() -> Settings:
    return load_settings(os.environ)     # load_settings(env) stays pure and testable
```

### Choosing your setup

Every option here is a trade-off:

| Pattern | ✅ | ❌ |
|---|---|---|
| Simple factory | one place for creation logic | grows an `if` chain |
| Registry | extensible without editing the factory | registration happens at import — modules must be imported; name clashes |
| Builder | readable, validated, immutable results | more code than a constructor for simple objects |
| Singleton class | guaranteed single instance | global state, testing pain, concurrency surprises |
| Cached getter / DI | explicit, resettable | someone must wire it (composition root) |

- ✅ Factory/registry: choosing implementations from config or input (exporters, payment gateways, LLM providers).
- ✅ Builder: many optional parts + invariants; test data builders.
- ✅ Shared instance: expensive clients (DB engine, HTTP session) — created once in the app factory and injected.
- 🚫 A factory for a class with one implementation and no configuration.
- 🚫 A builder for a 3-field object — use a dataclass.
- 🚫 Singletons for things tests need to vary (settings, clocks, repositories).

## ⚠️ Common mistakes

- Patterns as decoration: `AbstractExporterFactoryManager` for two classes.
- Registries that silently overwrite existing names.
- Builders that allow `build()` to return invalid objects.
- Module-level `settings = Settings()` reading production env vars during tests.

:::revoshop
(1) RevoShop's `config/__init__.py` has `config_by_name = {"development": DevelopmentConfig, "production": ProductionConfig}` — that's a **registry**. What happens with an unknown `FLASK_ENV` value, and how would you make the error helpful? (2) `create_app()` is an application **factory** ✅ — but `config/base.py` calls `load_dotenv()` and reads env vars **at import time**. Why can that surprise tests? (3) Find the seeders: would a `ProductBuilder` make test data clearer than long constructor calls?
:::

## 🏆 Best practices

- [ ] Keep creation logic in **one** place (a factory function, registry or composition root).
- [ ] Make "unknown option" errors helpful: list the valid choices.
- [ ] Builders return **immutable** objects and validate in `build()`.
- [ ] Prefer keyword arguments + dataclass validation before inventing a builder.
- [ ] No side effects at import time: no connecting, no reading env into globals.
- [ ] Replace singletons with **cached factory functions** or **dependency injection**; make caches resettable for tests.
- [ ] Name patterns in code reviews only when it adds clarity — never force a pattern.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a junior developer why "just make Settings a Singleton" makes tests flaky, and what `@functools.cache` + `cache_clear()` gives you instead.

## 📐 Design it

CareerPilot's AI features (Phase 3) must support several LLM providers: Anthropic (default), OpenAI, and a local Ollama model for offline development — plus a fake for tests. The provider and model come from settings; each provider client is expensive to create. Design how the right client is created, shared and swapped in tests.

:::quiz
Show a possible design

```python
class LLMClient(Protocol):
    def complete(self, messages: list[Message], *, max_tokens: int) -> Completion: ...

LLM_PROVIDERS: dict[str, Callable[[Settings], LLMClient]] = {}

def register_provider(name):                    # registry decorator
    def decorator(factory): LLM_PROVIDERS[name] = factory; return factory
    return decorator

@register_provider("anthropic")
def _anthropic(settings): return AnthropicClient(api_key=settings.llm_api_key, model=settings.llm_model)

@register_provider("ollama")
def _ollama(settings): return OllamaClient(base_url=settings.ollama_url, model=settings.llm_model)

def create_llm_client(settings: Settings) -> LLMClient:   # factory with a helpful error
    try: return LLM_PROVIDERS[settings.llm_provider](settings)
    except KeyError: raise ValueError(f"unknown provider {settings.llm_provider!r} (available: ...)") from None
```

- **Shared**: `create_app()` (the composition root) calls `create_llm_client(settings)` **once** and stores it in the service container / `app.extensions`; services receive it via their constructor. No global singleton.
- **Tests**: construct services with `FakeLLMClient(responses=[...])` directly — no env vars, no network.
- **Swapping**: change `LLM_PROVIDER=ollama` in `.env` for offline development; production uses Anthropic.
- **Extending**: adding a provider = one registered factory function.
:::

### 📝 Self-review checklist

- [ ] One creation point, driven by settings
- [ ] Expensive client created once without a global singleton
- [ ] Tests inject a fake without patching globals
- [ ] New providers don't modify existing code

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/d-design-patterns/01-creational" ai="no-ai" title="Registry factory, validating builder and a testable singleton"}
Build an exporter registry with a decorator and helpful errors, a fluent `JobPostingBuilder` that validates cross-field rules and returns frozen postings, and a cached `get_settings()` that tests can reset — with nothing created at import time.
:::

:::hints
- The registry decorator is a function returning a function that receives the class.
- In the builder, store parts in private attributes; only `build()` creates the dataclass.
- `raise ValueError(...) from None` hides the internal `KeyError` from the error message chain.
- `@cache` on a zero-argument function turns it into a lazily created shared value.
:::

## ✅ Quick check

:::quiz
What problem does a registry solve that an `if/elif` factory doesn't?

New implementations can be added by registering them, without modifying the factory function (open/closed).
:::

:::quiz
Name two reasons a classic Singleton makes testing harder.

It's hidden global state shared between tests, and it's hard to replace or reset with test-specific values (often created at import time).
:::


## 📚 Keep learning

- [Refactoring.Guru — Creational patterns](https://refactoring.guru/design-patterns/creational-patterns)
- [Python docs: functools.cache](https://docs.python.org/3/library/functools.html#functools.cache)
- [Flask docs: Application Factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
