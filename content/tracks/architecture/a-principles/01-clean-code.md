---
title: "Clean Code: Names, Small Functions, Clear Intent"
summary: Write code that a teammate (or you in 3 months) understands in one read — naming, function size, comments that matter.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: optional }
durationMinutes: 90
tags: [architecture, clean-code, naming, refactoring]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why code is read far more often than it's written
- Naming rules that remove the need for most comments
- Keeping functions small and at **one level of abstraction**
- Which comments help and which ones hurt
- Refactoring safely: tests first, small steps

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Clean code** | Code the next person understands in one read | Kode yang mudah dibaca |
| **Intent** | What the code is *trying* to do, not how | Maksud kode |
| **Level of abstraction** | How zoomed-in the code is: strategy vs tiny details | Tingkat kedalaman detail |
| **Guard clause** | Handling the odd case first and returning early | Keluar awal untuk kasus khusus |
| **Magic number** | An unexplained number in the code (`* 0.11`) | Angka tanpa penjelasan |
| **Refactor** | Improving the code without changing what it does | Merapikan tanpa mengubah perilaku |
| **Code smell** | A sign that something will hurt later | Tanda kode bermasalah |

## 🧠 The big idea

Code has two audiences: the **computer** (which runs anything that's valid) and **humans** (who have to understand, change and fix it). Clean code optimizes for the humans.

A good kitchen has labeled jars and one tool per drawer. You can cook in a messy kitchen too — but every meal takes longer and someone eventually uses salt instead of sugar.

## ❓ Why it matters

- Teams spend most of their time **reading** existing code before changing it.
- Unclear code causes bugs, because people misunderstand what it does.
- In interviews and code reviews, readability is judged as seriously as correctness.

It's the kitchen argument: you *can* cook in a messy kitchen, but every meal takes longer, and sooner or later someone reaches for salt and gets sugar.

## 📖 Step by step

### 1. Names reveal intent

A good name saves a comment and a question. `days_since_applied` needs no explanation; `d` needs a paragraph.

```python
def total_discounted_revenue(orders: list[Order], minimum_amount: int) -> int:
    revenue = 0
    for order in orders:
        if order.is_paid and order.amount > minimum_amount:
            revenue += member_price(order) if order.is_member else order.amount
    return revenue
```

| Rule | ❌ | ✅ |
|---|---|---|
| Say what it **is** | `d`, `data`, `info` | `orders`, `job_listings` |
| Booleans read as yes/no | `flag`, `status` | `is_paid`, `has_access`, `can_edit` |
| Functions are **verbs** | `total()`, `user()` | `calculate_total()`, `find_user()` |
| No magic numbers | `* 0.9` | `MEMBER_DISCOUNT = 0.10` |
| Consistent vocabulary | `get_user`, `fetch_account`, `load_member` for the same idea | pick one: `get_…` |
| Length fits scope | `the_list_of_all_active_users_in_system` | short in small scopes (`i` in a 3-line loop), descriptive in big ones |

### 2. Small functions, one job

A function should do **one thing**, at **one level** of detail:

```python
def import_jobs(path: str) -> ImportResult:
    rows = read_csv_rows(path)
    jobs = [parse_job(row) for row in rows]
    valid_jobs = [job for job in jobs if is_valid(job)]
    save_jobs(valid_jobs)
    return ImportResult(imported=len(valid_jobs), skipped=len(jobs) - len(valid_jobs))
```

You can read `import_jobs` like a table of contents. Details live in the named helpers. Mixing levels — "open a file", then "compute the salary median", then "format a date string" in one function — forces the reader to jump between big picture and tiny details.

Signs a function does too much: it's longer than one screen, has several blank-line "sections", its name needs *and*, or it takes more than ~4 parameters.

### 3. Comments: explain **why**, not **what**

```python
# ❌ Noise: repeats the code
i += 1  # increment i

# ❌ Lie waiting to happen: code changes, comment doesn't
# Returns the top 3 skills
def top_skills(n): ...

# ✅ Why: context the code can't express
# The payment provider retries webhooks for 24h, so we must ignore duplicates by event id.
if event.id in processed_event_ids:
    return
```

If you need a comment to explain **what** a block does, try extracting it into a function whose **name** says it.

### 4. Guard clauses and flat code

(You met these in the Conditionals lesson.) Handle invalid cases early, keep the main path unindented.

### 5. Refactor safely

Tests first, then small steps. Refactoring without tests is rearranging the kitchen in the dark — it may be tidier, and you won't know what you broke.

:term[Refactoring]{bahasa="refactoring — memperbaiki struktur kode tanpa mengubah perilakunya"} = changing structure **without** changing behavior.

1. Make sure **tests** cover the behavior (write them if missing).
2. Change **one** thing (rename, extract a function).
3. Run the tests.
4. Commit. Repeat.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Many tiny functions | Readable names, easy tests | Too many jumps if split mechanically (3-line functions used once everywhere) |
| Long descriptive names | Self-documenting | Can get unwieldy — rename the concept instead |
| Refactoring now | Easier future changes | Time now; risk without tests |
| "It works, don't touch it" | No immediate risk | Every future change gets slower and riskier |

- ✅ Rename and extract whenever you've just understood confusing code — leave it clearer than you found it.
- ✅ Refactor **before** adding a feature to messy code, with tests.
- 🚫 Don't refactor code without tests covering it.
- 🚫 Don't mix a big refactor and a behavior change in one commit/PR — reviewers can't tell them apart.


## ⚠️ Common mistakes

- Abbreviations only you understand (`usr_mgr_svc`).
- Names that lie (`get_user()` that also creates one).
- Comment blocks explaining messy code instead of cleaning it.
- Giant "utils.py" files where everything goes.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why "code that works" isn't the same as "good code", using an analogy from their daily life (a shared kitchen, a messy spreadsheet, handwriting…).

## 📐 Design it

Rewrite the `calc(d, t)` function from the top of this lesson with good names, a named constant and — if helpful — a small helper function. Assume each `x` is a tuple `(order_id, amount, is_paid, is_member)`.

:::quiz
Show a possible rewrite

```python
MEMBER_DISCOUNT_RATE = 0.9

def revenue_above(orders: list[tuple[str, int, bool, bool]], minimum_amount: int) -> float:
    revenue = 0.0
    for _order_id, amount, is_paid, is_member in orders:
        if is_paid and amount > minimum_amount:
            revenue += charged_amount(amount, is_member)
    return revenue

def charged_amount(amount: int, is_member: bool) -> float:
    return amount * MEMBER_DISCOUNT_RATE if is_member else amount
```

Unpacking the tuple into names removes every `x[2]`-style guess.
:::

### 📝 Self-review checklist

- [ ] No single-letter names outside tiny loops
- [ ] The discount rate is a named constant
- [ ] Someone could read the function without any comment

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/a-principles/01-clean-code" ai="no-ai" title="Refactor a messy report"}
`report.py` contains one 40-line function with cryptic names that generates an application-status report for CareerPilot. The tests already pass — **keep them passing** while you refactor:

- rename everything to reveal intent
- replace magic values with constants
- extract at least 3 well-named helper functions
- no function longer than 15 lines, no single-letter names except `_` (a test checks)
:::

:::hints
- Run the tests after **every** small change.
- Start with renames (safest), then extract functions.
- Look for "sections" separated by blank lines — each is a candidate function.
:::

## ✅ Quick check

:::quiz
What's the difference between refactoring and rewriting?

Refactoring changes structure in small, behavior-preserving steps backed by tests. Rewriting replaces the code, often changing behavior, with much higher risk.
:::

:::quiz
When is a comment better than a better name?

When it explains **why** — a business reason, an external constraint, a non-obvious decision — which code alone can't express.
:::


## 📚 Keep learning

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Ruff — a fast Python linter & formatter](https://docs.astral.sh/ruff/)
