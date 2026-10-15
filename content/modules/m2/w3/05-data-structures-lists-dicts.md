---
title: "Data Structures: Lists, Dicts, Sets & Tuples"
summary: Choose the right built-in collection for the job, know their costs, and use the collections module and dataclasses for clearer data.
type: lesson
source: core
roles: { be: core, fe: optional, fs: core, ai: core, ops: recommended }
durationMinutes: 150
tags: [python, data-structures, dict, set, collections, dataclasses]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What `list`, `tuple`, `dict` and `set` are **for** — and their performance costs
- Everyday dict and set operations you'll use in APIs
- `collections`: `Counter`, `defaultdict`, `deque`, `namedtuple`
- Representing records: dicts vs **`dataclass`** vs `TypedDict`
- Nested data (JSON-like) without getting lost, and copying it safely

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **`list`** | An ordered, changeable sequence | Urutan yang bisa diubah |
| **`tuple`** | A fixed sequence you can't change | Urutan tetap |
| **`dict`** | Labelled values: look up by key | Pasangan kunci–nilai |
| **`set`** | A bag of unique values, fast for "is this in it?" | Kumpulan nilai unik |
| **Hashable** | A value stable enough to be a dict key or set member | Bisa jadi kunci |
| **O(1) vs O(n)** | Instant lookup vs checking every item | Langsung vs periksa semua |
| **`Counter`** | Counts how many times each value appears | Penghitung kemunculan |
| **`defaultdict`** | A dict that creates missing values for you | Dict dengan nilai awal otomatis |
| **`dataclass`** | A small class for records, with named fields | Kelas ringkas untuk data |
| **Deep copy** | A copy that doesn't share the nested pieces | Salinan hingga isi dalam |

## 🧠 The big idea

Picking a data structure is like picking a **container in a kitchen**:

| Container | Kitchen version | Python |
|---|---|---|
| A row of numbered jars you can rearrange | shelf | `list` |
| A sealed bento box with fixed compartments | lunch box | `tuple` |
| Labelled drawers ("spoons", "knives") | drawer cabinet | `dict` |
| A bag of unique ingredients — "do we have garlic?" | pantry check | `set` |

The right container makes the task obvious and fast; the wrong one makes simple things slow and awkward.

## ❓ Why it matters

Every API request and response is data: lists of jobs, a dict per job, sets of permissions, tuples of coordinates. Choosing well gives you **readable code** and **fast operations** — the Big-O you measured in the DSA track.

Choosing badly is quietly expensive:

```python
blocked_user_ids = [3, 17, 42, ...]          # 100,000 ids
for request in requests:                     # 10,000 requests
    if request.user_id in blocked_user_ids:  # O(n) scan each time → a billion comparisons
        reject(request)
```

```python
job = ["Backend Dev", "Kopi Data", 12000000, True]
salary = job[2]          # what's index 2? what if someone inserts a field?
```

The first is a list used where a set belongs (checking a guest list name by name instead of using an index). The second is data with no labels, so every reader must guess.

## 📖 Step by step

### 1. Costs at a glance

| Operation | `list` | `tuple` | `dict` | `set` |
|---|---|---|---|---|
| get by index | O(1) | O(1) | — | — |
| get by key | — | — | O(1) avg | — |
| `x in …` | **O(n)** | **O(n)** | O(1) avg (keys) | O(1) avg |
| append / add | O(1) | ✗ immutable | O(1) avg | O(1) avg |
| insert/remove at front | **O(n)** | ✗ | — | — |
| ordered | ✅ | ✅ | ✅ (insertion order) | ❌ |
| duplicates | ✅ | ✅ | unique keys | ❌ unique |
| hashable (usable as dict key) | ❌ | ✅ (if contents are) | ❌ | ❌ (`frozenset` ✅) |

### 2. Tuples: fixed records and dict keys

```python
point = (-6.2, 106.8)
lat, lng = point

visits: dict[tuple[str, str], int] = {}
visits[("Jakarta", "2026-09-13")] = 120      # composite key
```

### 3. Dicts: the backbone of backend Python

```python
job = {"title": "Backend Dev", "salary": 12_000_000}

job.get("city", "Remote")                 # default instead of KeyError
job.setdefault("skills", []).append("sql")
job |= {"remote": True}                   # merge/update (3.9+)
{**job, "salary": 13_000_000}             # new dict with a change (original untouched)

for key, value in job.items(): ...
{k: v for k, v in job.items() if v is not None}   # drop None values

by_id = {j["id"]: j for j in jobs}        # index for O(1) lookups
```

### 4. Sets: membership and comparisons

A set answers "is this in it?" in one step, however big it is — which is why permission checks and blocklists belong in sets, not lists.

```python
required = {"python", "sql", "docker"}
mine = {"python", "sql", "react"}

required & mine        # {'python', 'sql'}      intersection — what I have
required - mine        # {'docker'}             difference — what I'm missing
required | mine        # union
required <= mine       # False                  subset: do I have everything?

seen: set[str] = set()
if url in seen: ...    # O(1) duplicate check
```

### 5. The `collections` module

```python
from collections import Counter, defaultdict, deque, namedtuple

Counter(skills).most_common(3)                # counting (Module 1!)

by_city = defaultdict(list)                   # missing keys start as []
for job in jobs:
    by_city[job["city"]].append(job)

recent = deque(maxlen=100)                    # O(1) add/remove at both ends; keeps the last 100
recent.append(event)

Point = namedtuple("Point", "lat lng")        # tuple with names (dataclasses are usually nicer)
```

### 6. Records: dict, dataclass or TypedDict?

Rule of thumb: a dict for data passing through (JSON in, JSON out), a `dataclass` when the same shape travels through your own code and you want names, defaults and typos caught.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class JobListing:
    title: str
    company: str
    salary_max: int | None = None
    skills: tuple[str, ...] = ()
    tags: list[str] = field(default_factory=list)   # never a bare [] default

job = JobListing("Backend Dev", "Kopi Data", 12_000_000, ("python", "sql"))
job.title            # attribute access, autocomplete, typo-safe
```

| Record style | ✅ | ❌ |
|---|---|---|
| `dict` | flexible, maps directly to JSON | typos in keys found only at runtime; no autocomplete |
| `@dataclass` | clear fields, defaults, `__eq__`/`__repr__` for free, `frozen` immutability | convert to/from JSON yourself (`asdict`) |
| `TypedDict` | type-checks dict keys while staying a dict | no runtime validation |
| Pydantic model (Module 3) | runtime **validation** + JSON conversion | extra dependency |

A common shape: **dicts at the edges** (JSON in/out), **dataclasses/models inside** your business logic.

### 7. Nested data safely

```python
payload = {"user": {"profile": {"city": "Jakarta"}}}

city = payload.get("user", {}).get("profile", {}).get("city")   # no KeyError on missing levels
```

Copying (DSA Stage 1 recap): `dict.copy()` is shallow; nested dicts/lists are shared. Use `copy.deepcopy` or build new structures.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| `list` for lookups | simple | O(n) `in` |
| `set`/`dict` index | O(1) lookups | extra memory; no duplicates / needs hashable keys |
| `tuple` | immutable, hashable, lightweight | can't change; fields by position |
| `frozen` dataclass | safe to share, hashable | create a new object for changes (`dataclasses.replace`) |
| `defaultdict` | shorter grouping code | reading a missing key **creates** it silently |

- ✅ `set` for membership/uniqueness, `dict` for lookup by key, `list` for ordered sequences, `tuple` for fixed records and composite keys.
- ✅ Dataclasses for domain records passed around your code.
- 🚫 Don't use lists of pairs when you need lookups by key.
- 🚫 Don't use positional tuples for records with many fields — names prevent bugs.

## ⚠️ Common mistakes

- `x in big_list` inside loops.
- Mutable default fields in dataclasses (`tags: list = []` raises an error — for good reason).
- Using `defaultdict` and accidentally creating keys by reading them.
- Expecting `set` to keep order.
- Mutating a dict while iterating over it (`RuntimeError: dictionary changed size`).

:::revoshop
In RevoShop, find a place where a list of items is checked for membership or duplicates (e.g. cart items, product ids in an order, allowed roles). Would a `set` or a dict index make it clearer or faster? Also look at `app/schemas/` — marshmallow schemas turn dicts into validated data. How is that similar to a dataclass, and how is it different?
:::

## 🏆 Best practices

- [ ] Choose the collection by **the operations you need** (lookup, order, uniqueness, mutability).
- [ ] Build a `dict`/`set` **index** once when you'll look things up repeatedly.
- [ ] Use `dict.get` with defaults and `setdefault`/`defaultdict` for grouping.
- [ ] Use **`@dataclass`** (often `frozen=True, slots=True`) for internal records; `field(default_factory=list)` for mutable defaults.
- [ ] Keep JSON-shaped dicts at the boundaries; convert to typed objects inside.
- [ ] Prefer returning **new** collections over mutating inputs.
- [ ] Use set operations (`&`, `-`, `|`, `<=`) for permission and skill comparisons.
- [ ] Add type hints to collections: `list[JobListing]`, `dict[int, User]`, `set[str]`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why checking "is this ingredient in the pantry?" is fast with a labeled bag of unique items but slow with a long shopping receipt. Connect it to `set` vs `list`.

## 📐 Design it

For CareerPilot's **"skills gap"** feature, choose data structures for:
1. The skills required by one job
2. The user's skills
3. How many target jobs require each missing skill
4. A job listing record passed between functions
5. The last 50 viewed job ids (newest first, no duplicates)

:::quiz
Show a possible design

1. `frozenset[str]` (unique, hashable, compared with set operations)
2. `set[str]`
3. `Counter[str]` — for each job, `counter.update(job.required_skills - user_skills)`
4. `@dataclass(frozen=True, slots=True) class JobListing` with `required_skills: frozenset[str]`
5. A `deque(maxlen=50)` plus removal of the id before re-adding (small size makes `remove` cheap), or a `dict` used as an ordered set (`dict.fromkeys`) trimmed to 50.
:::

### 📝 Self-review checklist

- [ ] Uniqueness and membership use sets
- [ ] Counting uses `Counter`
- [ ] The record is typed and immutable
- [ ] I considered ordering and size limits for "recent items"

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w3/05-data-structures" ai="no-ai" title="Skills gap engine"}
Implement a small skills-gap engine in `skills_gap.py` with a frozen dataclass `JobListing`, set operations for matching, `Counter` for missing-skill demand, `defaultdict` for grouping, and a bounded "recently viewed" structure. One test checks that membership lookups stay fast on large inputs.
:::

:::hints
- `JobListing.from_dict(data)` should normalize skills to a `frozenset` of lowercase, stripped strings.
- Match score: `len(required & mine) / len(required)` — define what happens when a job requires nothing.
- `RecentlyViewed.add(id)` removes the id first if present, then appends to the left.
:::

### 🏆 Stretch goal

Add `to_dict()` on `JobListing` returning JSON-ready data (skills as a sorted list) using `dataclasses.asdict`, and a round-trip test.

## ✅ Quick check

:::quiz
Why can a tuple be a dict key but a list can't?

Dict keys must be hashable, which requires immutability. A tuple (of hashable items) can't change, so its hash stays valid; a list can.
:::

:::quiz
What does `required - mine` give you for two sets of skills?

The skills that are required but that you don't have (set difference).
:::

:::quiz
Why use `field(default_factory=list)` in a dataclass?

A plain `[]` default would be shared by every instance; `default_factory` creates a new list for each object (dataclasses even raise an error for mutable defaults).
:::


## 📚 Keep learning

- [Python tutorial: Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python docs: collections](https://docs.python.org/3/library/collections.html)
- [Python docs: dataclasses](https://docs.python.org/3/library/dataclasses.html)
