---
title: "Type Hints & Pydantic v2"
summary: The engine under FastAPI — Python type hints plus Pydantic v2 models that validate, coerce, and document your data, with Field constraints and custom validators that reject bad input before it reaches your logic.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 110
tags: [fastapi, pydantic, type-hints, validation, python]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- How Python **type hints** describe the shape of data
- What a **Pydantic** model is and how it validates and **coerces** data
- Adding rules with **`Field`** (min/max, length, defaults)
- Writing a **custom validator** for rules types can't express
- Why validating at the edge keeps your core logic clean

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Type hint** | Declaring a value's type (`age: int`) | Menyebut tipe nilai |
| **Pydantic** | A library that validates data against models | Pustaka validasi data |
| **Model** | A class describing expected fields and types | Kelas bentuk data |
| **Coerce** | Convert compatible input to the right type | Mengubah ke tipe yang tepat |
| **Field** | A helper to add rules to a model field | Penambah aturan field |
| **Validator** | Custom code that checks/cleans a value | Pengecek nilai buatan |
| **ValidationError** | The error Pydantic raises on bad data | Error saat data buruk |

## 🧠 The big idea

A Pydantic model is a **form with rules at the front desk**. Before a visitor (incoming data) reaches the office (your logic), the desk checks the form: name filled in? age a real number? email looks valid? A bad form is rejected right there with a clear note, so your office only ever deals with clean, correct data.

## ❓ Why it matters

Untrusted data — from users, other services, files — is where bugs and security holes start. If you validate scattered throughout your code, you'll miss cases and repeat yourself. Pydantic lets you declare the rules **once** as a model; it validates and **coerces** at the boundary and hands your logic a guaranteed-correct object. FastAPI uses exactly this for every request, so learning Pydantic is learning the engine.

## 📖 Step by step

### 1. Type hints: the vocabulary

```python
name: str
age: int
price: float
tags: list[str]
nickname: str | None = None      # optional, defaults to None
```

These describe *intent*. On their own Python doesn't enforce them at runtime — that's what Pydantic adds.

### 2. A Pydantic model validates and coerces

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    is_active: bool = True

User(name="Ismail", age="30")     # age "30" is coerced to int 30 ✅
User(name="Ismail", age="old")    # raises ValidationError ❌
```

- **Validation**: `age="old"` can't become an int → `ValidationError` with a clear message.
- **Coercion**: `age="30"` (a numeric string) becomes `30`. Pydantic is helpfully lenient with clearly-compatible input.

### 3. Field: rules beyond the type

`Field` adds constraints the bare type can't express:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)                 # must be > 0
    stock: int = Field(default=0, ge=0)        # >= 0, defaults to 0
```

Now `price=-5` is rejected automatically — a rule you'd otherwise hand-write everywhere.

### 4. Custom validators for real rules

Some rules need logic. Use a field validator:

```python
from pydantic import BaseModel, field_validator

class Signup(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_has_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("email must contain @")
        return v.lower()          # you can also clean/normalize
```

Validators can **reject** (raise `ValueError`) and **clean** (return a fixed value, like lowercasing).

### 5. Reading the error

A `ValidationError` tells you exactly what failed — field, rule, and value — which is what FastAPI turns into a `422` response body. You get precise, machine-readable errors for free.

### Choosing what to validate

| Rule | Use |
|---|---|
| "must be an int / str / list" | the type hint |
| "must be > 0", "length 1–100" | `Field(...)` constraint |
| "email has @", "end date after start" | a custom validator |
| Cleaning (trim, lowercase) | return a fixed value from a validator |

- ✅ Model every external input; validate at the boundary, not deep in logic.
- ✅ Prefer `Field` constraints and validators over scattered `if` checks.
- 🚫 Don't trust incoming data; don't re-validate the same thing in ten places.

## ⚠️ Common mistakes

- Skipping models and passing raw dicts around — validation gaps and no autocomplete.
- Re-checking values by hand *after* Pydantic already guaranteed them.
- Putting business rules that need a database inside a validator (keep those in services).
- Forgetting Pydantic **coerces** — `"30"` becoming `30` is a feature, but know it happens.
- Using Pydantic v1 patterns (`@validator`) — v2 uses `@field_validator` and `model_config`.

:::revoshop
RevoShop (Flask) uses Marshmallow schemas for validation. (1) Find a schema and rewrite it as a Pydantic model with `Field` constraints (e.g. `price > 0`, name length). (2) Where does RevoShop validate that would become a custom validator (e.g. an email or a status enum)? (3) What clean-up (trimming, lowercasing) could a validator centralize instead of repeating in routes?
:::

## 🏆 Best practices

- [ ] Define a Pydantic model for every external input and output shape.
- [ ] Express simple rules with `Field`; use `field_validator` for logic and cleaning.
- [ ] Validate once at the boundary; let the rest of the code trust the model.
- [ ] Return normalized values (trim/lowercase) from validators to keep data consistent.
- [ ] Use Pydantic v2 idioms (`field_validator`, `model_config`), not v1.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain a Pydantic model with the form-and-front-desk analogy. Then give one example each of a rule handled by the type, by `Field`, and by a custom validator.

## 📐 Design it

Design the Pydantic models for CareerPilot's "create application" input: `company` (non-empty, ≤120 chars), `role` (non-empty), `salary_expectation` (optional, if present must be ≥ 0), `status` (one of `saved`, `applied`, `interviewing`), and `contact_email` (must contain `@`, stored lowercase). Decide which rule each field uses and write the model.

:::quiz
Show a possible design

```python
from pydantic import BaseModel, Field, field_validator

class ApplicationIn(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1)
    salary_expectation: float | None = Field(default=None, ge=0)
    status: str
    contact_email: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed = {"saved", "applied", "interviewing"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("contact_email")
    @classmethod
    def email_ok(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("email must contain @")
        return v.lower()
```

- Types handle `company`/`role`/`salary` being the right kind of value.
- `Field` handles length and `ge=0` (and the optional default).
- Validators handle the `status` enum and the email rule + lowercasing.

**Rule shown:** match each rule to the simplest tool — type, then `Field`, then a validator — and normalize in the validator so downstream code gets clean data.
:::

### 📝 Self-review checklist

- [ ] Every field uses the simplest rule that fits (type → Field → validator)
- [ ] Optional fields have sensible defaults
- [ ] Enums/format rules handled by validators
- [ ] Values normalized (lowercase/trim) where useful

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w1/02-pydantic-models" ai="no-ai" title="Validate and clean with Pydantic v2"}
Build a `Product` model with `Field` constraints (name length, price > 0, stock ≥ 0) and a `Signup` model with a custom validator that requires `@` in the email and stores it lowercase. The tests parse valid data (including coercion of a numeric string) and assert `ValidationError` on each broken rule.
:::

:::hints
- `from pydantic import BaseModel, Field, field_validator, ValidationError`.
- `price: float = Field(gt=0)`, `name: str = Field(min_length=1, max_length=50)`, `stock: int = Field(ge=0)`.
- The email validator: `if "@" not in v: raise ValueError(...)` then `return v.lower()`.
- In tests, use `with pytest.raises(ValidationError):` for the failing cases.
:::

## ✅ Quick check

:::quiz
What is the difference between validation and coercion in Pydantic?

Validation rejects data that can't fit the model (raising `ValidationError`), while coercion converts clearly-compatible input to the declared type — e.g. the numeric string `"30"` becomes the int `30`. Coercion is a convenience; validation is the guarantee.
:::

:::quiz
When do you need a custom `field_validator` instead of a `Field` constraint?

When the rule needs logic a constraint can't express — checking an email contains `@`, ensuring an end date is after a start date, or normalizing a value (trimming, lowercasing). `Field` covers simple bounds (min/max, length, ≥/≤); validators cover everything else.
:::

## 📚 Keep learning

- [Pydantic v2: models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic v2: fields & constraints](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic v2: validators](https://docs.pydantic.dev/latest/concepts/validators/)
