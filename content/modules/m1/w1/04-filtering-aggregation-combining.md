---
title: "Filtering, Aggregation & Combining Algorithms"
summary: Turn raw records into answers — filter with comprehensions, group and summarize, and combine data from several sources.
type: lesson
source: core
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [algorithms, comprehensions, grouping, data-processing]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **Filter** and **transform** with list/dict comprehensions
- **Aggregate**: totals, averages, min/max per group ("group by")
- **Combine**: `zip`, joining two lists of records by id, merging dictionaries
- **De-duplicate** while keeping order
- How these map directly to SQL (`WHERE`, `GROUP BY`, `JOIN`) you'll write in Module 2

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Filter** | Keep only the items you want | Menyaring data |
| **Transform / map** | Reshape each item | Mengubah bentuk data |
| **Comprehension** | Filtering and transforming in one readable line | Satu baris penyaring dan pengubah |
| **Aggregate** | Summarise many rows into one number | Meringkas jadi satu nilai |
| **Group by** | Summarise per category (per city, per status) | Meringkas per kelompok |
| **Join** | Attach data from another source by a shared id | Menggabungkan sumber data |
| **`zip`** | Pair up two lists item by item | Memasangkan dua daftar |
| **De-duplicate** | Remove repeats, keeping the order | Membuang data ganda |
| **Lookup dict** | A dict built for fast joining | Kamus untuk pencocokan cepat |

## 🧠 The big idea

Data processing is a kitchen line:

1. **Filter** — throw away what you don't need (*"only remote jobs"*)
2. **Transform** — reshape what's left (*"just the title and salary"*)
3. **Group & aggregate** — summarize (*"average salary per city"*)
4. **Combine** — bring in another source (*"attach company ratings to each job"*)

Almost every report, dashboard or API response is some combination of these four steps.

## ❓ Why it matters

Raw data is never the answer. Somebody asks "what's the average salary per city for remote jobs?" and you have a list of 5,000 messy records. The path from one to the other is always the same kitchen line: filter → transform → group → combine.

There's a bonus: these four steps are exactly SQL's `WHERE`, `SELECT`, `GROUP BY` and `JOIN`, which you'll meet in Module 2. Doing them in Python first means SQL will feel familiar instead of foreign.

## 📖 Step by step

### 1. Comprehensions: filter + transform in one line

```python
prices = [45_000, 120_000, 30_000, 99_000]

cheap = [p for p in prices if p < 50_000]          # filter
with_tax = [p * 111 // 100 for p in prices]        # transform
cheap_with_tax = [p * 111 // 100 for p in prices if p < 50_000]   # both
```

Read it as: **[what to keep** `for` **each item** `in` **collection** `if` **condition]**.

Dict and set comprehensions work the same way:

```python
price_by_name = {item["name"]: item["price"] for item in items}
unique_cities = {job["city"] for job in jobs}
```

:::tip[Keep comprehensions simple]
One `for` and one `if` is great. If you need nested loops or several conditions, a normal `for` loop is usually easier to read.
:::

### 2. Built-in aggregations

```python
salaries = [job["salary"] for job in jobs]

total = sum(salaries)
average = sum(salaries) / len(salaries) if salaries else 0
highest_job = max(jobs, key=lambda job: job["salary"])   # the whole record, not just the number
any_remote = any(job["remote"] for job in jobs)
all_verified = all(job["verified"] for job in jobs)
```

### 3. Group by

The pattern is the counting dictionary again, with a list (or a running total) as the value instead of a number.

The counting pattern from Lesson 01, but collecting **values** instead of counts:

```python
sales = [("Jakarta", 100), ("Bandung", 50), ("Jakarta", 30)]

by_city: dict[str, list[int]] = {}
for city, amount in sales:
    by_city.setdefault(city, []).append(amount)   # create the list the first time
# {'Jakarta': [100, 30], 'Bandung': [50]}

summary = {
    city: {"total": sum(amounts), "count": len(amounts), "average": sum(amounts) / len(amounts)}
    for city, amounts in by_city.items()
}
```

`setdefault(key, [])` returns the existing list, or inserts and returns a new empty one. (`collections.defaultdict(list)` does the same automatically.)

### 4. Combining with `zip`

```python
names = ["Ana", "Budi", "Citra"]
scores = [88, 92, 79]

for name, score in zip(names, scores):
    print(name, score)

report = dict(zip(names, scores))   # {'Ana': 88, 'Budi': 92, 'Citra': 79}
```

`zip` stops at the **shortest** list — mismatched lengths are silently truncated. Use `zip(a, b, strict=True)` (Python 3.10+) to get an error instead.

### 5. Joining records by id

Build a lookup dictionary first, then walk the other list once. Looping inside a loop to match ids is the O(n²) version of the same job.

Build an **index** of one side (Lesson 02!), then look up for each record of the other side:

```python
companies = [{"id": 1, "name": "Nusantara Tech"}, {"id": 2, "name": "Kopi Data"}]
jobs = [{"title": "Backend Dev", "company_id": 2}, {"title": "QA", "company_id": 3}]

company_by_id = {c["id"]: c for c in companies}

joined = []
for job in jobs:
    company = company_by_id.get(job["company_id"])
    joined.append({**job, "company": company["name"] if company else None})
```

`{**job, "company": ...}` creates a **new** dict with all of `job`'s fields plus one more — the original stays unchanged.

| Join type | Keep jobs without a matching company? | SQL name |
|---|---|---|
| Keep all jobs, `None` when missing | ✅ | `LEFT JOIN` |
| Keep only jobs that have a company | ❌ | `INNER JOIN` |

### 6. Merging dictionaries

```python
defaults = {"page": 1, "per_page": 20, "sort": "newest"}
user_choice = {"per_page": 50}

settings = defaults | user_choice   # {'page': 1, 'per_page': 50, 'sort': 'newest'}
```

On key conflicts, the **right side wins**.

### 7. De-duplicate while keeping order

```python
seen = set()
unique = []
for email in emails:
    key = email.strip().lower()
    if key not in seen:
        seen.add(key)
        unique.append(email)
```

`list(set(emails))` also removes duplicates but **loses the order** (and can't normalize).

### The same ideas in SQL (preview)

| Python | SQL (Module 2) |
|---|---|
| `[j for j in jobs if j["remote"]]` | `SELECT * FROM jobs WHERE remote = true` |
| group by + `sum` | `SELECT city, SUM(amount) FROM sales GROUP BY city` |
| index + lookup | `SELECT ... FROM jobs LEFT JOIN companies ON ...` |

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Comprehension | Short, clear for simple rules | Unreadable when nested |
| Explicit loop | Room for comments and several steps | Longer |
| Join with nested loops | No setup | n × m steps |
| Join with an index dict | ~n + m steps | Memory for the index |
| Process in Python | Flexible, easy to test | Slow and memory-hungry for millions of rows |
| Process in the database | Fast, uses indexes | Needs SQL; logic spread across layers |

- ✅ Separate steps: `filter → transform → aggregate → format`. Each can be a small pure function.
- ✅ Decide explicitly what happens with **missing matches** (LEFT vs INNER join behavior).
- 🚫 Don't load a whole database table into Python just to filter it — use `WHERE`.
- 🚫 Don't compute an average of an empty list without a guard.


## ⚠️ Common mistakes

- `zip` silently dropping items when lists have different lengths.
- Modifying records while joining (mutating shared dicts) instead of creating new ones.
- `ZeroDivisionError` on averages of empty groups.
- Using `list(set(...))` when order matters.
- Comprehensions so long they need horizontal scrolling.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain "group by" using a real example like sorting receipts into envelopes per month and then totaling each envelope. Then explain the difference between keeping or dropping jobs whose company can't be found.

## 📐 Design it

Design a **"Salary insights"** report for CareerPilot from `jobs` (title, city, salary, remote, company_id) and `companies` (id, name, rating). The report should show, per city: number of jobs, average salary, the highest-paying job title with its company name, and the share of remote jobs (%).

Write the steps as a pipeline and name each function.

:::quiz
Show a possible design

```text
1. valid_jobs     = filter_jobs_with_salary(jobs)                  # drop salary=None
2. company_by_id  = index_by_id(companies)
3. enriched       = attach_company_names(valid_jobs, company_by_id) # LEFT JOIN, name=None if missing
4. groups         = group_by(enriched, key="city")
5. insights       = {city: summarize(city_jobs) for city, city_jobs in groups.items()}
   summarize → count, average salary, top job (title + company), remote share
6. formatted      = format_report(insights)                         # sorted by average salary desc
```

Each step is a pure function you can test on its own with 3–4 hand-written records.
:::

### 📝 Self-review checklist

- [ ] Filtering happens before the expensive steps
- [ ] The join uses an index, not nested scanning
- [ ] Missing companies and empty groups are handled
- [ ] Formatting is separate from calculation

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

## 🧸 Job market insights

:::exercise{path="exercises/m1/w1/04-filter-aggregate" ai="no-ai" title="Filter, group, join"}
In `insights.py` implement:

- `remote_titles(jobs, min_salary)` → titles of remote jobs with `salary >= min_salary`, in original order (use a comprehension)
- `group_by_city(jobs)` → `{city: [jobs...]}`
- `city_summary(jobs)` → `{city: {"count": int, "average_salary": int, "remote_share": int}}` — average rounded down to whole rupiah, remote share as a whole percentage (rounded down)
- `attach_company(jobs, companies)` → new job dicts with a `"company"` key holding the company name, or `None` if not found (don't modify the input dicts)
- `unique_emails(emails)` → de-duplicated case-insensitively, keeping the **first** spelling and original order
:::

:::hints
- `setdefault(city, []).append(job)` for grouping.
- Remote share: `remote_count * 100 // count`.
- Index companies first: `{c["id"]: c for c in companies}`.
- `{**job, "company": name}` copies a dict with an extra key.
:::

### 🏆 Stretch goal

Add `top_company_per_city(jobs, companies)` returning the company with the highest **average** salary per city. Reuse your other functions.

## ✅ Quick check

:::quiz
Rewrite as a comprehension: collect `name.upper()` for every name longer than 3 characters.

`[name.upper() for name in names if len(name) > 3]`
:::

:::quiz
What does `list(zip([1, 2, 3], ["a", "b"]))` return, and why can that be dangerous?

`[(1, 'a'), (2, 'b')]` — the extra `3` is silently dropped. Use `strict=True` to catch mismatched lengths.
:::

:::quiz
Why build a dictionary index before joining two lists of records?

So each lookup is ~1 step instead of scanning the other list for every record (n × m steps).
:::


## 📚 Keep learning

- [Python tutorial: List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [Python docs: zip](https://docs.python.org/3/library/functions.html#zip)
- [Python docs: collections.defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict)
