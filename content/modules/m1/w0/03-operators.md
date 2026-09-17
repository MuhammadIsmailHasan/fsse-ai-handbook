---
title: "Operators: Arithmetic, Comparison, and Logic"
summary: Calculate, compare and combine conditions — including the operators beginners misuse most (//, %, and, or).
type: lesson
source: core
sourceRef: "M1 · W0 · L2"
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 120
tags: [python, operators, boolean-logic]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Arithmetic operators, including `//` (floor division) and `%` (remainder)
- Comparison operators and why they always give `True` or `False`
- Logic with `and`, `or`, `not` — and **short-circuiting**
- Operator **precedence** and when to add parentheses

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Operator** | A symbol that does something to values (`+`, `==`) | Simbol operasi |
| **Arithmetic** | Maths: `+ - * /` | Perhitungan |
| **`//` floor division** | Divide and throw away the remainder | Bagi lalu bulatkan ke bawah |
| **`%` modulo** | The remainder after dividing | Sisa bagi |
| **Comparison** | Asking a yes/no question (`>`, `==`) | Perbandingan |
| **`=` vs `==`** | Assign a value / check if equal | Memberi nilai / membandingkan |
| **Logic (`and`, `or`, `not`)** | Combining yes/no answers | Menggabungkan kondisi |
| **Short-circuit** | Python stops early when the answer is already decided | Berhenti lebih awal |
| **Precedence** | Which operator runs first | Urutan pengerjaan |

## 🧠 The big idea

An :term[operator]{bahasa="operator — simbol yang melakukan aksi pada nilai, seperti + atau =="} is a tiny machine: values go in, a new value comes out.

- **Arithmetic** machines output numbers: `3 + 4` → `7`
- **Comparison** machines output a yes/no: `3 > 4` → `False`
- **Logic** machines combine yes/no answers: `True and False` → `False`

Every "decision" in software — *can this user check out? is this password long enough?* — is built from these three.

## ❓ Why it matters

Business rules are maths and logic wearing a costume:

- "free shipping over Rp 200.000" → a comparison,
- "an admin **or** the owner may edit" → logic,
- "show 20 items per page" → division and remainder,
- "is this password long enough **and** does it have a number?" → both.

Getting these wrong is quiet and expensive: `=` instead of `==`, or an `and` where an `or` belongs, produces code that runs happily and gives the wrong answer.

## 📖 Step by step

### 1. Arithmetic

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` `-` `*` | add, subtract, multiply | `7 * 3` | `21` |
| `/` | division (always a float) | `7 / 2` | `3.5` |
| `//` | floor division — whole part only | `7 // 2` | `3` |
| `%` | remainder (modulo) | `7 % 2` | `1` |
| `**` | power | `2 ** 10` | `1024` |

`//` and `%` are a pair — they answer "how many **whole** groups, and how many **left over**?"

```python
items = 23
per_box = 5
full_boxes = items // per_box    # 4
left_over = items % per_box      # 3
```

Classic uses of `%`: even/odd (`n % 2 == 0`), "every 3rd row" (`i % 3 == 0`), wrapping around (`(index + 1) % len(items)`).

Shortcut assignment: `total += price` means `total = total + price`. Also `-=`, `*=`, `//=`.

### 2. Comparison

| Operator | Meaning |
|---|---|
| `==` | equal |
| `!=` | not equal |
| `<` `<=` `>` `>=` | less / greater (or equal) |
| `in` | is inside (a string, list, …) |

```python
print(5 == 5.0)                 # True
print("Jakarta" == "jakarta")   # False — text comparison is case-sensitive
print("@" in "ana@mail.com")    # True
print(18 <= 20 < 65)            # True — Python lets you chain comparisons
```

### 3. Logic

| Operator | True when… |
|---|---|
| `a and b` | **both** are true |
| `a or b` | **at least one** is true |
| `not a` | `a` is false |

Truth table:

| a | b | `a and b` | `a or b` |
|---|---|---|---|
| True | True | True | True |
| True | False | False | True |
| False | True | False | True |
| False | False | False | False |

### 4. Short-circuiting

This is why `if user and user.is_active:` is safe: if `user` is `None`, Python never looks at `.is_active`. Checking the gate before opening it.

Python stops evaluating as soon as the answer is known:

- `False and anything` → `False` (right side never runs)
- `True or anything` → `True` (right side never runs)

This is useful to avoid errors:

```python
# If items is empty, len(items) > 0 is False and items[0] is never touched.
if len(items) > 0 and items[0] == "urgent":
    ...
```

### 5. Precedence: who goes first

When in doubt, add brackets. Nobody has ever complained that a condition was too easy to read.

From highest to lowest (simplified):

1. `**`
2. `*` `/` `//` `%`
3. `+` `-`
4. comparisons `<` `==` `in` …
5. `not`
6. `and`
7. `or`

```python
print(2 + 3 * 4)          # 14, not 20
print(True or False and False)   # True — `and` binds tighter than `or`
```

:::tip[The readability rule]
If **you** had to think about precedence, add parentheses. Your future teammates will thank you.
`(age < 18) or (is_student and age < 25)`
:::

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| One long boolean expression | Compact | Hard to read and debug |
| Named intermediate variables (`is_adult = age >= 18`) | Self-documenting, easy to print | A few more lines |
| Relying on short-circuit to avoid errors | Concise | Order of conditions becomes important — reordering can crash |
| `/` then `int()` vs `//` | — | `int(-7 / 2)` is `-3` but `-7 // 2` is `-4`: they differ for negatives |

- ✅ Use `//` and `%` for grouping, pagination (`page_count = (total + per_page - 1) // per_page`), and cycles.
- ✅ Give complex conditions a **name**.
- 🚫 Don't compare booleans to `True`: write `if is_member:` not `if is_member == True:`.
- 🚫 Don't compare floats with `==` after math (`0.1 + 0.2 == 0.3` is `False`). Use `math.isclose()`.


## ⚠️ Common mistakes

- `=` (assign) instead of `==` (compare).
- `if x == 1 or 2:` — always true! It means `(x == 1) or 2`. Write `if x in (1, 2):`.
- Expecting `/` to return an `int`.
- Mixing `and`/`or` without parentheses.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain `//` and `%` using a real-life example that has nothing to do with programming (eggs in cartons, students in groups…). Then explain short-circuiting as if to a friend.

## 📐 Design it

Write a **single, readable** boolean expression (you may use named variables) for this rule from an online course platform:

> A user can watch a lesson if they **bought the course**, **or** the lesson is marked **free preview**. Admins can watch everything. Banned users can watch nothing — not even free previews, and not even if they're admins.

:::quiz
Show a possible design

```python
is_allowed_normally = has_purchased or is_free_preview or is_admin
can_watch = is_allowed_normally and not is_banned
```

Naming the middle step makes the "banned beats everything" rule obvious.
:::

### 📝 Self-review checklist

- [ ] My analogy for `//` and `%` gives the same numbers as Python would
- [ ] My expression gives `False` for a banned admin
- [ ] I used parentheses or named variables instead of relying on precedence

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

## 🧸 Checkout calculator

:::exercise{path="exercises/m1/w0/03-operators" ai="no-ai" title="Checkout rules"}
In `checkout.py`, implement the rules of a small online shop:

- `split_bill(total, people)` → `(each, remainder)` as whole rupiah
- `page_count(total_items, per_page)` → how many pages a list needs
- `is_even(n)` → `True`/`False`
- `gets_free_shipping(cart_total, is_member, is_oversized)` → members with carts **≥ Rp 500.000** get free shipping, but **never** for oversized items
:::

:::hints
- `split_bill` is a direct use of `//` and `%`.
- For pages, think: 10 items, 3 per page → 4 pages. Try `(total_items + per_page - 1) // per_page`. Why does that work?
- Even numbers leave no remainder when divided by 2.
- Build `gets_free_shipping` from three facts combined with `and` and `not`.
:::

### 🏆 Stretch goal

Add `shipping_fee(weight_kg)`: Rp 10.000 for the first kg (or part of it), plus Rp 5.000 for **each started** extra kg. `0.5` → `10000`, `1` → `10000`, `1.2` → `15000`, `3` → `20000`.

## ✅ Quick check

:::quiz
What do `-7 // 2` and `-7 % 2` return?

`-4` and `1`. Floor division rounds **down** (towards negative infinity), and the remainder keeps the sign of the divisor so that `(-4 * 2) + 1 == -7`.
:::

:::quiz
Why is `if role == "admin" or "owner":` a bug?

It's read as `(role == "admin") or "owner"`. The non-empty string `"owner"` is truthy, so the condition is **always** true. Use `role in ("admin", "owner")`.
:::

:::quiz
How can the order of conditions in an `and` prevent a crash?

With short-circuiting, the right side runs only if the left side is true — e.g. `user is not None and user.is_active` never touches `user.is_active` when `user` is `None`.
:::


## 📚 Keep learning

- [Python docs: Operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence)
- [Python docs: Boolean operations](https://docs.python.org/3/reference/expressions.html#boolean-operations)
