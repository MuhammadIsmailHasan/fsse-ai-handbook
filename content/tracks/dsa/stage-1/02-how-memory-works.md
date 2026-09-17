---
title: "How Memory Works: References, Mutability & Copies"
summary: Why changing one list sometimes changes "another" — references, mutable vs immutable values, and shallow vs deep copies.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 120
tags: [dsa, memory, references, mutability]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Variables hold **references** (arrows), not boxes of data
- **Mutable** vs **immutable** types, and why it matters
- **Aliasing** bugs: two names, one object
- Shallow vs deep **copies**
- How Python lists are stored (dynamic arrays) and why `append` is fast but `insert(0, …)` is slow

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Reference** | A name pointing at an object, not holding a copy of it | Penunjuk ke objek |
| **Aliasing** | Two names pointing at the same object | Dua nama, satu objek |
| **Mutable** | Can be changed in place (list, dict, set) | Bisa diubah isinya |
| **Immutable** | Cannot be changed; you get a new object (str, tuple, int) | Tidak bisa diubah |
| **`is` vs `==`** | Same object vs same value | Objek sama vs nilai sama |
| **Shallow copy** | A new outer container, sharing the inner objects | Salinan lapisan luar |
| **Deep copy** | A copy all the way down, sharing nothing | Salinan sampai isi dalam |
| **Dynamic array** | How a Python list grows: extra space at the end | Larik yang bisa membesar |
| **Garbage collection** | Python freeing objects nothing points at any more | Pembersihan memori otomatis |

## 🧠 The big idea

In Python, a variable is an **arrow** pointing at an object in memory — not a box that contains it.

```python
a = [1, 2, 3]
b = a          # b points at THE SAME list
b.append(4)
print(a)       # [1, 2, 3, 4] 😮
```

```mermaid
flowchart LR
    a((a)) --> L["list object: [1, 2, 3, 4]"]
    b((b)) --> L
```

Two names, one list. Change it through either name and both "see" the change. That's :term[aliasing]{bahasa="aliasing — dua nama variabel menunjuk objek yang sama di memori"}.

## ❓ Why it matters

Copying big data every time you pass it to a function would be slow and waste memory, so Python passes **references**: cheap and fast — and surprising if you don't know it.

This is behind some of the most confusing bugs beginners meet:

- You "copy" a list, change the copy, and the original changes too.
- A function is supposed to just read a dict, but the caller's data comes back modified.
- A default argument `def add(item, cart=[])` keeps items from the previous call, because the list was created once.

Knowing that a name is an arrow, not a box, explains all three at once.

## 📖 Step by step

### 1. `==` vs `is`

```python
a = [1, 2]
b = [1, 2]
c = a
print(a == b)   # True  — same VALUE
print(a is b)   # False — different OBJECTS
print(a is c)   # True  — same object
```

Use `==` to compare values. Use `is` only for singletons like `None`: `if value is None:`.

### 2. Mutable vs immutable

| Immutable (can't change in place) | Mutable (can change in place) |
|---|---|
| `int`, `float`, `bool`, `str`, `tuple`, `None` | `list`, `dict`, `set`, most objects |

"Changing" an immutable value actually creates a **new** object and moves the arrow:

```python
name = "ana"
other = name
name = name.upper()     # new string "ANA"; `name` now points at it
print(other)            # "ana" — unaffected
```

With mutable objects, methods like `.append()` change the **same** object — every alias sees it.

### 3. Function arguments are references too

```python
def add_bonus(salaries):
    salaries.append(1_000_000)    # mutates the caller's list!

def with_bonus(salaries):
    return salaries + [1_000_000] # creates a NEW list; caller's list untouched
```

Prefer functions that **return new data** unless mutation is the explicit purpose (and the name says so).

### 4. Shallow vs deep copy

A shallow copy is a **new envelope with the same photos inside**: tear one photo and both envelopes show the damage. A deep copy photocopies the photos too.

```python
import copy

original = [[1, 2], [3, 4]]

shallow = original.copy()        # or list(original), original[:]
shallow[0].append(99)
print(original)                  # [[1, 2, 99], [3, 4]] — inner lists are SHARED

deep = copy.deepcopy(original)
deep[0].append(42)
print(original)                  # unchanged
```

| Copy | Copies | Nested objects |
|---|---|---|
| Assignment `b = a` | nothing | shared |
| Shallow `a.copy()` | the outer container | **still shared** |
| Deep `copy.deepcopy(a)` | everything, recursively | independent |

Build grids safely: `grid = [[0] * 3 for _ in range(3)]` — a **new** row list each time.

### 5. How lists live in memory

This is why `append` is cheap and `insert(0, …)` is not: adding at the end uses space that is already reserved, while adding at the front shifts every other item one place along.

A Python list is a **dynamic array**: a block of slots in a row, each holding a reference.

```text
index:   0     1     2     3    [spare][spare]
       [ → ] [ → ] [ → ] [ → ]
```

- `items[i]` → jump straight to slot i → **O(1)**
- `append(x)` → use a spare slot → **O(1)** (occasionally the array grows into a bigger block, but on average it's still O(1))
- `insert(0, x)` / `pop(0)` → shift **every** element one slot → **O(n)**

Need fast adds/removes at **both** ends? Use `collections.deque`.

### 6. Garbage collection

When no arrows point to an object anymore, Python frees its memory automatically. You rarely manage memory by hand in Python — but you do need to know **who else is pointing** at your data.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Mutate in place | No copying, low memory | Surprises for other references |
| Return new objects | Predictable, easy to test | Extra memory and copying time |
| Shallow copy | Cheap | Nested data still shared |
| Deep copy | Fully independent | Slow and memory-heavy for big structures |
| Tuples instead of lists for fixed data | Can't be mutated by accident | Can't be changed when you need to |

- ✅ Treat input arguments as **read-only** by default.
- ✅ Use tuples or frozen data for values that should never change (config, constants).
- ✅ Mutate in place deliberately for performance on large data — and document it.
- 🚫 Never use mutable default arguments.
- 🚫 Don't `deepcopy` "just in case" on large data in hot paths.


## ⚠️ Common mistakes

- `b = a` and believing `b` is a copy.
- `[[0] * n] * n` for grids.
- Shallow-copying nested dicts, then modifying inner values.
- Using `is` to compare strings or numbers.
- Mutating a list while iterating over it.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain aliasing using a real-life analogy (e.g. two people sharing one Google Doc link vs. one person downloading a copy). Then explain why a shallow copy of a list of lists is like copying a **table of contents** but still sharing the chapters.

## 📐 Design it

Predict the output **before** running anything:

```python
settings = {"theme": "dark", "tags": ["a"]}
backup = settings.copy()
settings["theme"] = "light"
settings["tags"].append("b")
print(backup)
```

Then redesign the code so `backup` is completely unaffected.

:::quiz
Show the answer

Output: `{'theme': 'dark', 'tags': ['a', 'b']}`. The shallow copy has its own `"theme"` entry (reassigning the key doesn't affect it), but both dicts point at the **same** `tags` list.

Fix: `backup = copy.deepcopy(settings)` — or make `tags` a tuple so it can't be mutated.
:::

### 📝 Self-review checklist

- [ ] I predicted before running
- [ ] I can explain why `"theme"` differs but `"tags"` doesn't
- [ ] My fix makes nested data independent

::ai-review{task="explain"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s1-no-surprise-mutation" title="No Surprise Mutations" difficulty="easy" path="exercises/dsa/stage-1/03-no-surprise-mutation"}
Fix three functions that accidentally modify their inputs or share state: `add_tag`, `make_grid`, and `apply_raise`. The tests check both the results **and** that inputs stay unchanged.
:::

:::problem{id="dsa-s1-reverse-in-place" title="Reverse In Place" difficulty="easy" path="exercises/dsa/stage-1/04-reverse-in-place"}
Reverse a list **in place** using O(1) extra space — no slicing, no `reversed()`, no `.reverse()`, no new list. Swap from both ends towards the middle.
:::

:::hints
- `add_tag`: return `tags + [tag]` instead of appending.
- `make_grid`: a comprehension creates a new row each time.
- Reverse: two indexes, `left` starting at 0 and `right` at the end. Swap with `a, b = b, a`. Stop when they meet.
:::

## ✅ Quick check

:::quiz
After `x = [1]; y = x; x = x + [2]`, what is `y`?

`[1]`. `x + [2]` creates a **new** list and reassigns `x`. `y` still points at the original. (With `x.append(2)` or `x += [2]`, `y` would change too.)
:::

:::quiz
Why is `pop(0)` on a large list slow?

Every remaining element has to shift one slot left: O(n). Use `collections.deque.popleft()` for O(1).
:::

:::quiz
When should you use `is` instead of `==`?

To check identity with singletons like `None` (`x is None`). For values — numbers, strings, lists — use `==`.
:::


## 📚 Keep learning

- [Python docs: copy — shallow and deep copy](https://docs.python.org/3/library/copy.html)
- [Python Tutor — visualize references step by step](https://pythontutor.com/)
