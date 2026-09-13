---
title: "Python Setup & Pythonic Syntax"
summary: Beyond "it runs" — the Python data model in one page, idiomatic syntax, PEP 8 with Ruff, and the habits that make code review go smoothly.
type: lesson
source: core
sourceRef: "M2 · W3 · L1"
split: true
roles: { be: core, fe: optional, fs: core, ai: core, ops: recommended }
durationMinutes: 120
tags: [python, pep8, ruff, idioms]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- How Python actually runs your code (interpreter, REPL, virtual environment recap)
- The **"everything is an object"** model: names, objects, mutability
- **Pythonic** idioms: unpacking, f-strings, truthiness, `enumerate`, `zip`, comprehensions, `with`
- **PEP 8** and automatic enforcement with **Ruff**
- **EAFP** vs **LBYL** — the Python way of handling "what if it isn't there?"

## 🧠 The big idea

Two sentences can mean the same thing, but one sounds natural to native speakers. :term[Pythonic]{bahasa="Pythonic — gaya menulis yang wajar dan idiomatis menurut komunitas Python"} code is Python written the way experienced Python developers expect to read it. It's not about being clever — it's about being **instantly understood** by the next person.

## ❓ Why does this exist?

Python has many ways to do the same thing. Teams need a shared style so that:
- code reviews focus on logic, not formatting,
- anyone can read anyone's code quickly,
- common bugs (mutable defaults, `== None`, shadowed built-ins) get caught automatically.

## 💥 What happens if we DON'T write Pythonic code?

```python
i = 0
result = []
while i < len(jobs):
    if jobs[i]["remote"] == True:
        if len(jobs[i]["skills"]) != 0:
            result.append(jobs[i]["title"].upper())
    i = i + 1
```

It works — and it's five potential bugs long (off-by-one, `== True`, index errors). The Pythonic version:

```python
result = [job["title"].upper() for job in jobs if job["remote"] and job["skills"]]
```

## 📖 How it works, step by step

### 1. Running Python

| Way | When |
|---|---|
| `uv run python` / `python` (REPL) | quick experiments; `help(obj)`, `dir(obj)` |
| `uv run python script.py` | run a file |
| `uv run python -m package.module` | run a module inside a package (Lesson 09) |
| IPython / Jupyter | exploration, data work |

### 2. Names point to objects

Recap from DSA Stage 1: variables are **names bound to objects**. Every object has a **type**, a **value**, and an **identity**.

```python
a = [1, 2]
b = a            # same object
b.append(3)      # a is [1, 2, 3] too
a is b           # True — identity
a == [1, 2, 3]   # True — equality
```

Use `is` only for singletons: `if value is None:`.

### 3. Idioms you'll use every day

```python
# Unpacking
first, *rest = ["python", "sql", "docker"]
lat, lng = coordinates
name, _ = full_name.split(" ", 1)          # _ = "ignored"

# Swap without a temp variable
a, b = b, a

# enumerate and zip instead of index loops
for position, job in enumerate(jobs, start=1): ...
for name, score in zip(names, scores, strict=True): ...

# Truthiness
if skills:                                  # not: if len(skills) != 0
    ...

# Conditional expression
label = "Remote" if job["remote"] else job["city"]

# Chained comparison
if 0 <= score <= 100: ...

# dict.get with default, setdefault
count = counts.get(skill, 0)

# f-strings with formatting and debugging
print(f"{salary:,}")        # 12,000,000
print(f"{ratio:.1%}")       # 45.3%
print(f"{job_id=}")         # job_id=42

# Context managers close resources for you
with open("jobs.csv", encoding="utf-8") as file:
    header = file.readline()

# any / all with generators
has_python = any("python" in job["skills"] for job in jobs)
```

### 4. EAFP vs LBYL

| Style | Meaning | Example |
|---|---|---|
| **LBYL** — Look Before You Leap | check first | `if key in data: value = data[key]` |
| **EAFP** — Easier to Ask Forgiveness than Permission | try, handle the specific failure | `try: value = data[key] except KeyError: …` |

Python often prefers EAFP, especially where the check and the action could race (files, network, databases): the file can disappear between `os.path.exists()` and `open()`.

```python
try:
    config = json.loads(path.read_text())
except FileNotFoundError:
    config = DEFAULT_CONFIG
```

### 5. PEP 8 in one table

| Thing | Style |
|---|---|
| variables, functions | `snake_case` |
| classes | `PascalCase` |
| constants | `UPPER_SNAKE_CASE` |
| private-ish | `_leading_underscore` |
| indentation | 4 spaces |
| line length | ~88–120 chars (team choice) |
| imports | top of file: standard library, third-party, local — separated by blank lines |
| comparisons | `is None`, `is not None`; never `== True` |

### 6. Let Ruff do it

[Ruff](https://docs.astral.sh/ruff/) is a very fast linter **and** formatter:

```bash
uv add --dev ruff
uv run ruff format .          # format code
uv run ruff check . --fix     # lint and auto-fix what's safe
```

```toml
# pyproject.toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]   # errors, pyflakes, isort, bugbear, pyupgrade, simplify
```

`B` (bugbear) catches things like mutable default arguments; `UP` modernizes syntax; `SIM` suggests simpler code.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Comprehension | concise, fast | unreadable when nested or with side effects |
| Explicit loop | room for steps and comments | longer |
| EAFP | no race between check and action; clean happy path | exceptions as control flow can hide logic if overused |
| LBYL | explicit | races for external resources; duplicate lookups |
| Strict lint rules | catches bugs early | initial noise on old code |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Use idioms that make intent obvious (`enumerate`, unpacking, `any`, `with`).
- ✅ Automate style with a formatter + linter in the editor **and** CI.
- 🚫 Don't write one-liners that need a comment to explain them.
- 🚫 Don't use comprehensions for side effects (`[print(x) for x in items]`).

## 🏆 Best practices

- [ ] Format with **`ruff format`** and lint with **`ruff check`** (or Black + Flake8) — same config locally and in CI.
- [ ] Follow **PEP 8** naming; never shadow built-ins (`list`, `dict`, `id`, `type`, `input`).
- [ ] `is None` / `is not None`; truthiness for empty checks.
- [ ] Use `with` for files, locks, database sessions — anything that must be closed.
- [ ] Prefer `enumerate`/`zip(strict=True)` over index arithmetic.
- [ ] Always pass `encoding="utf-8"` when opening text files.
- [ ] Keep comprehensions to one `for` and one `if`; otherwise use a loop.
- [ ] Target a modern Python (3.12+) and let `ruff`'s `UP` rules modernize syntax.

## 🏭 How it's used in industry

- Python teams almost universally run a formatter and linter in **pre-commit hooks** and CI; unformatted code simply fails the pipeline.
- Code review comments like "use `enumerate`", "this shadows `id`", "prefer `is None`" are exactly what linters automate.
- Readable Python matters even more with AI coding tools: you must quickly verify generated code.

## ⚠️ Common mistakes

- `== None`, `== True`.
- Mutable default arguments.
- Variables named `list`, `dict`, `str`, `id`.
- Opening files without `with` or `encoding`.
- Clever one-liners nobody can debug.

:::revoshop
RevoShop has `.pylintrc` and a *Code Quality & Security* section in its README. Run `pylint app` (or `uv run ruff check app` if you try Ruff) in the repo. Pick **three** warnings and explain what each one protects against. Do you find any shadowed built-ins (`id`, `type`, `filter`) in your routes or services?
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain EAFP vs LBYL using a real-life example (e.g. checking if a shop is open before walking there, versus walking there and handling "closed"). When does "check first" fail in software?

## 📐 Design it

Rewrite this function in Pythonic style and list every improvement you made:

```python
def summary(data):
    output = ""
    count = 0
    for i in range(len(data)):
        if data[i]["salary"] != None:
            if data[i]["remote"] == True:
                count = count + 1
                output = output + str(count) + ". " + data[i]["title"] + "\n"
    if len(output) == 0:
        return "No remote jobs with salary"
    return output
```

:::quiz
Show a possible rewrite

```python
def summary(jobs: list[dict]) -> str:
    matches = [job for job in jobs if job["salary"] is not None and job["remote"]]
    if not matches:
        return "No remote jobs with salary"
    return "".join(f"{number}. {job['title']}\n" for number, job in enumerate(matches, start=1))
```

Improvements: descriptive names; `is not None`; truthiness instead of `== True`/`len() == 0`; filtering separated from formatting; `enumerate(start=1)` instead of a manual counter; f-strings instead of concatenation; `"".join` instead of repeated string building; type hints.
:::

### 📝 Self-review checklist

- [ ] No index-based loops left
- [ ] Filtering and formatting are separate steps
- [ ] I can name each improvement and why it matters

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w3/01-pythonic-syntax" ai="no-ai" title="Make it Pythonic"}
`legacy.py` contains four working but un-Pythonic functions. Rewrite them in `pythonic.py` with the same behavior. Tests check behavior **and** style: no `range(len(...))`, no `== None`/`== True`, no shadowed built-ins, and files opened with `with` and `encoding`.
:::

:::hints
- Copy one function at a time, run the tests, then refactor it.
- `enumerate(items, start=1)` replaces manual counters.
- `" ".join(parts)` builds strings from lists.
- The tests use Python's `ast` module to spot `range(len(...))`.
:::

### 🏆 Stretch goal

Add Ruff to the exercises project (`uv add --dev ruff`) and make `uv run ruff check m2/w3/01-pythonic-syntax --select E,F,B,UP,SIM` pass on your file.

## ✅ Quick check

:::quiz
Why is `if skills:` preferred over `if len(skills) > 0:`?

It's shorter, idiomatic, and works for any collection (lists, dicts, sets, strings) and for `None` checks combined with emptiness.
:::

:::quiz
What does `zip(a, b, strict=True)` add?

It raises `ValueError` if the iterables have different lengths, instead of silently dropping extra items.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Idiomatic / Pythonic | Sesuai gaya alami bahasa |
| Linter / Formatter | Pemeriksa kode / Perapi format otomatis |
| PEP 8 | Panduan gaya resmi Python |
| EAFP / LBYL | Coba dulu, tangani error / Cek dulu sebelum bertindak |
| Shadowing | Menimpa nama bawaan dengan variabel sendiri |

## 📚 Keep learning

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Python glossary: EAFP](https://docs.python.org/3/glossary.html#term-EAFP)
