---
title: "DRY, KISS, YAGNI: Three Rules Against Wasted Effort"
summary: Avoid duplicated knowledge, needless complexity and features nobody asked for — and learn when each rule is wrong.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: optional }
durationMinutes: 90
tags: [architecture, dry, kiss, yagni, design-principles]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **DRY** — Don't Repeat Yourself (knowledge, not just lines)
- **KISS** — Keep It Simple
- **YAGNI** — You Aren't Gonna Need It
- The **Rule of Three** for when to remove duplication
- Why applying these rules blindly causes new problems

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **DRY** | Don't repeat the same *knowledge* in several places | Jangan ulangi pengetahuan |
| **KISS** | Keep it simple: the plainest thing that works | Buat sesederhana mungkin |
| **YAGNI** | Don't build what nobody has asked for yet | Jangan bangun yang belum perlu |
| **Rule of Three** | Wait until something appears three times before extracting it | Aturan tiga kali |
| **Accidental duplication** | Code that looks the same but means different things | Mirip tapi beda makna |
| **Premature abstraction** | Creating a shared helper too early, and regretting it | Penyatuan terlalu dini |
| **Over-engineering** | Building for imaginary future needs | Terlalu rumit untuk kebutuhan kini |

## 🧠 The big idea

All three rules protect the same thing: **your future time**.

| Rule | The waste it prevents |
|---|---|
| **DRY** | Fixing the same bug in 5 places (and missing one) |
| **KISS** | Spending a day understanding something that could be 10 obvious lines |
| **YAGNI** | Building, testing and maintaining features nobody ends up using |

## ❓ Why it matters

Software changes constantly. Every duplicated rule, clever trick and "we might need it" feature makes the **next** change slower and riskier. These three short names are lessons the industry learned the hard way.

| Rule | The waste it prevents |
|---|---|
| **DRY** | Fixing the same bug in five places — and missing one |
| **KISS** | Spending a day understanding what could have been ten obvious lines |
| **YAGNI** | Building, testing and maintaining features nobody ends up using |

But each rule has a failure mode too: DRY applied to code that only *looks* similar creates a shared function with five flags; KISS used as an excuse skips necessary structure; YAGNI taken to the extreme ignores changes you already know are coming.

## 📖 Step by step

### 1. DRY is about **knowledge**, not text

```python
TAX_RATE_PERCENT = 11                      # one source of truth

def add_tax(amount: int) -> int:
    return amount * (100 + TAX_RATE_PERCENT) // 100
```

Every place that needs tax calls `add_tax`. Change the rule once.

But two pieces of code that **look** the same can represent **different** knowledge:

```python
def max_username_length() -> int:
    return 30

def max_cart_items() -> int:
    return 30
```

These are not duplication — they'll change for different reasons. Merging them into `MAX_THINGS = 30` would couple unrelated rules. **Ask: "If one changes, must the other change too?"** Only then is it real duplication.

### 2. The Rule of Three

Two similar pieces of code might be a coincidence; three is a pattern. Waiting for the third saves you from merging two things that were never really the same.

- **1st time**: just write it.
- **2nd time**: notice the duplication, tolerate it.
- **3rd time**: extract the shared piece — now you know what actually varies.

Extracting too early often produces the **wrong abstraction**: a function with 7 flags trying to serve cases that turned out to be different.

:::tip
Duplication is cheaper than the wrong abstraction. It's easy to merge similar code later; it's painful to untangle a bad shared function used in 20 places.
:::

### 3. KISS: the simplest thing that works

Prefer, in order:

1. Built-in language features and the standard library
2. A few clear functions
3. A class, if there's real state and behavior to group
4. A pattern or framework, if a real, present problem needs it

```python
# ❌ Clever
is_weekend = bool((date.weekday() + 2) // 7)

# ✅ Simple
is_weekend = date.weekday() >= 5   # Saturday=5, Sunday=6
```

Simple ≠ easy to write. Simple = **easy to understand and change**. It often takes more thought.

### 4. YAGNI: build for today's requirements

When tempted to add something "because we might need it":

- Is there a user or ticket asking for it **now**?
- What does it cost to add **later**, when needed? (Usually: not much more.)
- What does it cost to carry **until** then? (Code to read, test, secure, migrate.)

YAGNI does **not** mean "write code that's impossible to extend". Clean, well-named, tested code is easy to extend later. It means: don't build the extension **before** it's needed.

### Choosing your setup

Every option here is a trade-off:

| Principle | Taken too far | Balance |
|---|---|---|
| DRY | Everything shares one mega-function; unrelated rules coupled | Extract duplicated **knowledge**; Rule of Three |
| KISS | "Simple" hacks that ignore real requirements (no error handling) | Simplest solution that meets **actual** requirements |
| YAGNI | Ignoring known, near-term needs; painting yourself into a corner | Don't build it — but don't block it either |

Security, data integrity and backups are **not** YAGNI. "We'll add authentication later" is how breaches happen.

- ✅ DRY for business rules, constants, validation, formatting.
- ✅ KISS by default, especially while learning and prototyping.
- ✅ YAGNI for features, configuration options and "flexibility".
- 🚫 Don't DRY up test code so much that each test becomes hard to read — some repetition in tests is healthy.
- 🚫 Don't use YAGNI as an excuse to skip validation, tests or security.


## ⚠️ Common mistakes

- Merging code that merely looks alike.
- Adding boolean flags to a shared function for every new case (`def send(email, is_invoice, is_reminder, skip_footer, …)`).
- Building a "framework" for your first project.
- Premature optimization as a form of complexity.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain YAGNI with a real-life analogy (packing for a trip, building a house, buying kitchen gadgets). Then explain why duplicated **knowledge** is worse than duplicated **lines**.

## 📐 Design it

For each situation, decide: apply DRY, KISS, YAGNI, or **leave it alone**. Justify in one sentence.

1. The email format validation regex appears in the sign-up, profile edit and admin user-create endpoints.
2. A teammate proposes an abstract `NotificationChannel` class hierarchy with Email, SMS, WhatsApp and Push. The product currently only sends email.
3. Two test functions each build a similar `user` dict with 5 fields.
4. You wrote a 3-line list comprehension; a teammate suggests replacing it with a custom `Pipeline().filter().map().collect()` class.
5. `MAX_UPLOAD_MB = 10` and `MAX_ATTACHMENTS = 10` — someone wants one constant.

:::quiz
Show possible answers

1. **DRY** — same knowledge (what a valid email is) in three places; extract `is_valid_email`.
2. **YAGNI** — one channel today; a simple `send_email` function is enough. Add structure when a second channel is actually needed.
3. **Leave it (mostly)** — small repetition keeps tests readable; a tiny helper/fixture is fine if it grows.
4. **KISS** — the comprehension is clear and standard; the custom class adds complexity for no benefit.
5. **Leave it alone** — same number, different knowledge; they'll change for different reasons.
:::

### 📝 Self-review checklist

- [ ] I asked "does this represent the same knowledge?" for DRY decisions
- [ ] I separated "might need" from "needed now"
- [ ] I noticed that some duplication is acceptable

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/a-principles/02-dry-kiss-yagni" ai="no-ai" title="Remove duplicated knowledge"}
`notifications.py` builds three kinds of CareerPilot reminder messages. Each function copy-pastes the same greeting, date formatting, and signature — with small inconsistencies (one is even a bug the tests reveal).

Refactor so that:
- greeting, date formatting and signature each live in **exactly one** helper
- the three public functions keep their names and signatures
- all tests pass, including the one exposing the inconsistency
:::

:::hints
- Run the tests first — one fails because one copy formats dates differently from the others.
- Extract `format_date(d)`, `greeting(name)`, `signature()`; then rebuild each message from them.
- Resist adding a generic `build_message(kind, **options)` with flags — three small functions are simpler (KISS).
:::

## ✅ Quick check

:::quiz
Two functions have identical bodies. Should you always merge them?

No — only if they represent the same knowledge and should change together. Identical code with different reasons to change should stay separate.
:::

:::quiz
What is the Rule of Three?

Tolerate duplication the first two times; extract a shared abstraction on the third, when you can see what really varies.
:::


## 📚 Keep learning

- [Martin Fowler: Yagni](https://martinfowler.com/bliki/Yagni.html)
- [Sandi Metz: The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
