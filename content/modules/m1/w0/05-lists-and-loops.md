---
title: "Lists and Loops: Repeating Work"
summary: Store many values in a list and process them with for and while loops — the accumulator pattern you'll use every day.
type: lesson
source: core
sourceRef: "M1 · W0 · L4"
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [python, lists, loops, iteration]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Create, read, change and slice **lists**
- Loop with `for`, `range()`, `enumerate()` and `while`
- The **accumulator pattern** (total, count, max, collect)
- `break`, `continue`, and how to avoid infinite loops

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **List** | Many values in order, under one name | Kumpulan nilai berurutan |
| **Index** | The position of an item, starting at 0 | Nomor posisi |
| **Slice** | Taking a piece of a list (`items[1:4]`) | Potongan daftar |
| **Loop** | Doing the same work for each item | Perulangan |
| **`for` loop** | Walk through every item | Ulangi untuk tiap item |
| **`while` loop** | Keep going while a condition is true | Ulangi selama syarat benar |
| **`range()`** | A sequence of numbers to loop over | Deret angka |
| **Accumulator** | A variable that builds up a result (total, count, list) | Penampung hasil |
| **`break` / `continue`** | Stop the loop / skip to the next item | Hentikan / lewati |
| **Infinite loop** | A `while` whose condition never becomes false | Perulangan tak berujung |

## 🧠 The big idea

A :term[list]{bahasa="list/daftar — kumpulan nilai yang berurutan dalam satu variabel"} is a **train**: one name, many carriages in order, each with a number starting from **0**.

A :term[loop]{bahasa="perulangan — menjalankan blok kode yang sama berkali-kali"} is a **conveyor belt**: it brings you each carriage one by one so you can do the same job on each.

Real apps are mostly lists and loops: a list of products → show each; a list of orders → sum totals; a list of messages → find unread ones.

## ❓ Why it matters

Data arrives in groups: 30 students, 1,000 transactions, 50 job listings. You can't create a thousand variables (`price1`, `price2`, …), and you can't paste the same line a thousand times — especially when you don't know **how many** there will be until the program runs.

Lists hold the group; loops do the same job to each member. Almost every screen you'll build later is this: a list of products → show each one; a list of orders → add up the totals; a list of messages → find the unread ones.

## 📖 Step by step

### 1. Lists

```python
fruits = ["apple", "banana", "cherry"]

print(fruits[0])      # "apple"   — first item is index 0
print(fruits[-1])     # "cherry"  — negative index counts from the end
print(len(fruits))    # 3

fruits.append("durian")        # add to the end
fruits.insert(1, "avocado")    # insert at position 1
fruits.remove("banana")        # remove first matching value
last = fruits.pop()            # remove and return the last item
fruits[0] = "apricot"          # replace

print("cherry" in fruits)      # True
```

**Slicing** gives you a piece (a new list): `list[start:stop]`, where `stop` is **not** included.

```python
numbers = [10, 20, 30, 40, 50]
print(numbers[1:3])   # [20, 30]
print(numbers[:2])    # [10, 20]    first two
print(numbers[-2:])   # [40, 50]    last two
print(numbers[::-1])  # [50, 40, 30, 20, 10]  reversed copy
```

### 2. `for` loops

```python
for fruit in fruits:
    print(fruit.upper())
```

Read it as: "for **each** fruit in fruits, do the indented block". The variable `fruit` holds the current item.

Need the position too? Use `enumerate`:

```python
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}. {fruit}")
```

Need to repeat a number of times? Use `range`:

```python
for i in range(3):        # 0, 1, 2
    print("Hello", i)

for i in range(2, 10, 2): # 2, 4, 6, 8   (start, stop, step)
    print(i)
```

### 3. The accumulator pattern

This is the shape behind most "reports": start with an empty basket, walk the list, put things in. Total, count, largest, or a new filtered list — same pattern, different basket.

Almost every loop does one of these four jobs. Learn the shapes:

```python
prices = [45_000, 120_000, 30_000, 99_000]

# 1. TOTAL: start at 0, add each
total = 0
for price in prices:
    total += price

# 2. COUNT: start at 0, add 1 when something matches
expensive = 0
for price in prices:
    if price > 50_000:
        expensive += 1

# 3. BEST SO FAR: start with the first item, replace when you find better
highest = prices[0]
for price in prices:
    if price > highest:
        highest = price

# 4. COLLECT: start with an empty list, append matches
cheap = []
for price in prices:
    if price < 50_000:
        cheap.append(price)
```

:::tip
Python has built-ins for the common cases: `sum(prices)`, `max(prices)`, `min(prices)`, `len(prices)`. Write the loops yourself **first** so you understand what they do — then use the built-ins in real code.
:::

### 4. `while` loops

`while` repeats **as long as** a condition is true. Use it when you don't know in advance how many times:

```python
balance = 1_000_000
months = 0
while balance > 0:
    balance -= 150_000
    months += 1
print(months)   # 7
```

:::danger[Infinite loops]
If the condition never becomes false, the loop never ends. Always make sure something **inside** the loop moves you towards stopping. Stuck? Press `Ctrl + C` in the terminal.
:::

### 5. `break` and `continue`

```python
for order in orders:
    if order == "CANCELLED":
        continue          # skip this one, go to the next item
    if order == "STOP":
        break             # leave the loop completely
    process(order)
```

### 6. Don't change a list while looping over it

Removing carriages while walking the train makes you skip some. Build a new list instead, or loop over a copy.

```python
numbers = [1, 2, 2, 3]
for n in numbers:
    if n == 2:
        numbers.remove(n)   # 🐛 skips items because positions shift
print(numbers)              # [1, 2, 3]  — one 2 survived!
```

Build a **new** list instead: `numbers = [n for n in numbers if n != 2]` (that's a *list comprehension* — you'll use them a lot in Week 1).

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| `for item in items` | Clear, can't go out of range | No index (use `enumerate`) |
| `for i in range(len(items))` | Have the index | Noisier, easy off-by-one mistakes |
| `while` | Flexible stopping condition | Risk of infinite loops |
| Built-ins (`sum`, `max`) | Short and fast | Hide the logic while learning |
| Modify in place | Saves memory | Surprising bugs when looping |

- ✅ `for` when you're going through a collection or a known number of steps.
- ✅ `while` for "until something happens": retries, reading until the end, game loops.
- 🚫 Don't use a list when you need to look things up by name — that's a `dict` (Week 1).
- 🚫 Don't nest loops over big lists without thinking: 10,000 × 10,000 = 100 million steps (you'll learn *Big-O* in the DSA track).


## ⚠️ Common mistakes

- **Off-by-one**: `range(1, 10)` stops at 9. The last index is `len(items) - 1`.
- `max([])` crashes on an empty list — check emptiness first.
- Forgetting to update the variable in a `while` loop.
- Resetting the accumulator **inside** the loop (`total = 0` in the loop body).
- Removing items from a list while iterating over it.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the accumulator pattern using a real-life example — for instance, a cashier adding up a basket, or a teacher counting students who passed. Map each step (start value, what happens per item, final result) to the code shape.

## 📐 Design it

Before coding, write **pseudocode** (plain-language steps) for this problem:

> Given a list of daily step counts for a month, report: the total steps, the number of days you hit **10,000 or more**, your **longest streak** of consecutive 10,000+ days, and the list of day numbers (1-based) where you walked fewer than 3,000 steps.

:::quiz
Show possible pseudocode

```text
total = 0, goal_days = 0, current_streak = 0, best_streak = 0, lazy_days = []
for each (day_number starting at 1, steps) in the list:
    total += steps
    if steps >= 10000:
        goal_days += 1
        current_streak += 1
        best_streak = max(best_streak, current_streak)
    else:
        current_streak = 0
    if steps < 3000:
        add day_number to lazy_days
```

Notice: **one loop** handles all four answers. The streak needs two variables — the current run, and the best run so far.
:::

### 📝 Self-review checklist

- [ ] I identified which accumulator shape each answer uses
- [ ] My streak resets when the goal is missed
- [ ] Day numbers start at 1, not 0
- [ ] I considered an empty month (no data)

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

## 🧸 Cart and step tracker

:::exercise{path="exercises/m1/w0/05-lists-and-loops" ai="no-ai" title="Loop it"}
In `loops.py`, implement **without** `sum`, `max`, `min` or list comprehensions (write the loops yourself this time):

- `cart_total(prices)` → total of all prices
- `count_expensive(prices, limit)` → how many prices are **greater than** `limit`
- `highest_price(prices)` → the largest price, or `None` for an empty list
- `first_over(prices, limit)` → the first price over `limit`, or `None` (stop looping once found!)
- `longest_streak(steps, goal)` → the longest run of consecutive days with `steps >= goal`
:::

:::hints
- `highest_price`: guard against empty lists first, then use the "best so far" shape.
- `first_over`: you can `return` directly from inside the loop — that also stops it.
- `longest_streak`: keep `current` and `best`. When a day misses the goal, `current = 0`.
:::

### 🏆 Stretch goal

Add `chunk(items, size)` that splits a list into pieces: `chunk([1,2,3,4,5], 2)` → `[[1,2],[3,4],[5]]`. Use `range` with a step and slicing.

## ✅ Quick check

:::quiz
What does `list(range(5, 0, -2))` produce?

`[5, 3, 1]` — start at 5, stop **before** 0, step −2.
:::

:::quiz
Why is removing items from a list inside a `for` loop over the same list a bug?

Removing shifts the positions of later items, so the loop skips the item right after the removed one. Build a new list instead.
:::

:::quiz
When should you prefer `while` over `for`?

When you don't know how many repetitions you need in advance — you repeat until a condition changes (retries, reading input until "quit", paying off a balance).
:::


## 📚 Keep learning

- [Python tutorial: Lists](https://docs.python.org/3/tutorial/introduction.html#lists)
- [Python tutorial: for statements and range()](https://docs.python.org/3/tutorial/controlflow.html#for-statements)
