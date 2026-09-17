---
title: "Counting & Frequency Algorithms"
summary: Count occurrences with dictionaries — the pattern behind analytics, duplicate detection, and your CareerPilot skill report.
type: lesson
source: core
sourceRef: "M1 · W1 · L1"
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [algorithms, dictionaries, counting, python]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Use a **dictionary** as a tally counter
- Find the most (and least) frequent items, and handle ties
- Detect **duplicates** and find items that appear once
- Why one loop with a dict beats two nested loops
- `collections.Counter` — after you can do it by hand

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Dictionary (dict)** | Pairs of key → value, like a word and its meaning | Pasangan kunci dan nilai |
| **Key / value** | What you look up / what you get back | Yang dicari / yang didapat |
| **Frequency** | How many times something appears | Jumlah kemunculan |
| **Tally** | Adding one to a count | Menambah satu hitungan |
| **`get(key, 0)`** | Read a count, or 0 if the key isn't there yet | Ambil nilai atau 0 |
| **Tie** | Two items with the same count | Nilai seri |
| **Duplicate** | A value that appears more than once | Data ganda |
| **`Counter`** | Python's ready-made counting dictionary | Penghitung siap pakai |

## 🧠 The big idea

Imagine counting votes on a whiteboard during a class election. For each ballot you find the candidate's name and add a tally mark — adding the name first if it isn't on the board yet. At the end you read the board.

That whiteboard is a :term[dictionary]{bahasa="dictionary — kumpulan pasangan kunci-nilai, seperti kamus: kata → arti"}: **keys** are the names, **values** are the counts.

```python
votes = ["Ana", "Budi", "Ana", "Citra", "Ana", "Budi"]
tally = {}
for name in votes:
    tally[name] = tally.get(name, 0) + 1
print(tally)   # {'Ana': 3, 'Budi': 2, 'Citra': 1}
```

## ❓ Why it matters

Counting is behind more real features than any other algorithm: top skills in job listings, most-sold products, duplicate emails, error rates per endpoint, words in a document, votes per candidate.

The naive version — for each item, walk the whole list and count matches — is O(n²) and quietly dies on real data. The dictionary version is one pass: touch each item once, add a tally mark.

Learning to do it by hand first also means the later shortcuts (`Counter`, SQL's `GROUP BY`, pandas' `value_counts`) are things you understand rather than magic you copy.

## 📖 Step by step

### 1. Dictionary essentials

```python
stock = {"apple": 5, "banana": 0}

stock["cherry"] = 12          # add or overwrite
print(stock["apple"])         # 5
print(stock.get("durian"))    # None — .get() doesn't crash on missing keys
print(stock.get("durian", 0)) # 0 — with a default
print("banana" in stock)      # True — checks KEYS

for fruit, amount in stock.items():
    print(fruit, amount)
```

Looking up a key in a dict is **fast no matter how big the dict is** — Python jumps straight to it instead of scanning. That's the secret behind everything in this lesson.

### 2. The counting pattern

Three lines, and you'll reuse them for the rest of your career: look at the item, read its current count (0 if new), write the count back plus one.

```python
def count_items(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts
```

Read `counts.get(item, 0) + 1` as: "current count, or 0 if new — plus one".

### 3. Most frequent item (and ties)

```python
counts = {"python": 5, "sql": 5, "react": 3}

top_count = max(counts.values())                                 # 5
leaders = [skill for skill, c in counts.items() if c == top_count]
print(leaders)                                                   # ['python', 'sql']
```

`max(counts, key=counts.get)` returns just **one** key — whichever comes first. Decide on purpose what should happen with ties: return all? sort alphabetically?

### 4. Sorting by count

```python
ranking = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
# [('python', 5), ('sql', 5), ('react', 3)]
```

A `lambda` is a tiny unnamed function: `lambda pair: pair[1]` means "given a pair, use its second element". Sorting gets a full lesson next — for now, this recipe is enough.

### 5. Duplicates and uniques

```python
emails = ["a@x.com", "b@x.com", "a@x.com"]

counts = count_items(emails)
duplicates = [e for e, c in counts.items() if c > 1]   # ['a@x.com']
uniques    = [e for e, c in counts.items() if c == 1]  # ['b@x.com']

# Only need "is there ANY duplicate?" — a set is enough:
has_duplicates = len(set(emails)) != len(emails)       # True
```

A :term[set]{bahasa="set/himpunan — kumpulan nilai unik tanpa urutan"} keeps only unique values, and checking `x in some_set` is fast like a dict.

### 6. Counting by a property

The key doesn't have to be the item itself — it can be anything you derive from it: the city, the first letter, the month. That's `GROUP BY` before you've met SQL.

Often you count a **field** of each record, not the record itself:

```python
jobs = [
    {"title": "Backend Dev", "city": "Jakarta"},
    {"title": "Data Analyst", "city": "Bandung"},
    {"title": "QA Engineer", "city": "Jakarta"},
]
per_city = {}
for job in jobs:
    city = job["city"]
    per_city[city] = per_city.get(city, 0) + 1
# {'Jakarta': 2, 'Bandung': 1}
```

### 7. `collections.Counter`

Python's standard library has this built in:

```python
from collections import Counter

skills = ["python", "sql", "python", "react"]
c = Counter(skills)
print(c["python"])        # 2
print(c.most_common(2))   # [('python', 2), ('sql', 1)]
```

:::tip
Write the dictionary version until it's automatic (and in interviews, be ready to). In real projects, use `Counter` — it's clearer and well tested.
:::

### Choosing your setup

Every option here is a trade-off:

| Approach | Speed for n items | Memory | Notes |
|---|---|---|---|
| Nested loops | 🐢 n × n | Tiny | Only OK for very small lists |
| Dict counter | 🚀 ~n | One entry per distinct item | The default choice |
| `Counter` | 🚀 ~n | Same | Less code, extra helpers |
| Sort then count neighbours | n log n | Tiny extra | Useful when data is already sorted or memory is tight |

- ✅ Frequencies, histograms, "top N", duplicates, anagram checks.
- ✅ Normalize before counting (`.lower().strip()`), or `"Python"` and `"python "` count separately.
- 🚫 If you only need **yes/no** "seen before?", a `set` is simpler than counts.
- 🚫 For **huge** datasets in a database, let the database count (`GROUP BY` — Module 2).


## ⚠️ Common mistakes

- `counts[item] += 1` on a new key → `KeyError`. Use `.get(item, 0) + 1`.
- Forgetting to normalize text before counting.
- Using `max(..., key=...)` and silently ignoring ties.
- Counting inside a nested loop "because it works on my 5-item test".

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why counting with a "whiteboard of names" (a dictionary) is much faster than re-reading the entire list of votes for every single ballot. Use numbers to make the difference feel real.

## 📐 Design it

CareerPilot will read job listings where each has a `skills` field like `"Python, SQL, Docker"`. Design (in pseudocode) a function that returns the **top 5 skills** across all listings.

Decide: How do you split and clean each skill? How do you treat `"python"` vs `"Python "`? What happens with ties at position 5? What if a listing has no skills?

:::quiz
Show a possible design

```text
counts = empty dict
for each listing:
    if skills field is empty: skip
    for each raw_skill in skills.split(","):
        skill = raw_skill.strip().lower()
        if skill == "": skip
        counts[skill] = counts.get(skill, 0) + 1
ranking = sort counts by (count descending, skill name ascending)
return first 5 of ranking
```

The tie-break on **name** makes the output stable: running it twice always gives the same top 5.
:::

### 📝 Self-review checklist

- [ ] I normalize case and whitespace
- [ ] Empty skills and empty listings don't crash
- [ ] Ties are handled deliberately (and I can say how)
- [ ] My design uses one pass to count, not nested scanning

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

## 🧸 Tally everything

:::exercise{path="exercises/m1/w1/01-counting" ai="no-ai" title="Counting toolkit"}
In `counting.py` implement, **without** `collections.Counter`:

- `count_items(items)` → dict of item → count
- `most_frequent(items)` → list of the most frequent item(s), sorted A→Z; `[]` for empty input
- `first_duplicate(items)` → the first item that appears a **second** time while reading left to right, or `None`
- `count_skills(skill_strings)` → counts skills from strings like `"Python, SQL"`, case-insensitive and trimmed
- `top_skills(skill_strings, n)` → list of `(skill, count)` sorted by count desc, then skill A→Z, at most `n` items
:::

:::hints
- `first_duplicate`: walk the list with a `seen` set. The moment an item is already in `seen`, return it.
- `most_frequent`: find the highest count, collect all keys with that count, then `sorted(...)`.
- Sort by count descending and name ascending with `key=lambda pair: (-pair[1], pair[0])`.
- `"".split(",")` returns `[""]` — skip empty skills after stripping.
:::

### 🏆 Stretch goal

Add `are_anagrams(a, b)` that ignores spaces and case: `"Dormitory"` / `"Dirty room"` → `True`. Use your `count_items`.

## ✅ Quick check

:::quiz
What does `counts.get("x", 0) + 1` do when `"x"` isn't in `counts` yet?

`.get` returns the default `0`, so the expression is `1`. Assigning it back creates the key with count 1.
:::

:::quiz
Why is a dictionary counter roughly n steps while the nested-loop version is roughly n × n?

The dict version reads each item once and jumps directly to its counter. The nested version re-scans the entire list for every item.
:::

:::quiz
You only need to know whether a list contains any duplicate. What's the simplest approach?

Compare `len(set(items))` with `len(items)` — if the set is smaller, something repeated.
:::


## 📚 Keep learning

- [Python tutorial: Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
- [Python docs: collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)
