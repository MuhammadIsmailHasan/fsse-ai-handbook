---
title: "Data Containers: Variables & Data Types"
summary: How programs remember things — variables, Python's core data types, and converting between them safely.
type: lesson
source: core
split: true
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [python, variables, types]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **variable** really is in Python
- The core types: `int`, `float`, `str`, `bool`, `None` (plus a first look at `list` and `dict`)
- How to **check** a type and **convert** between types
- Why data from forms and files always arrives as **text**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Variable** | A name attached to a value | Nama untuk sebuah nilai |
| **Value** | The actual data (`450000`, `"Sari"`) | Datanya sendiri |
| **Data type** | What kind of value it is, and what you may do with it | Jenis nilai |
| **`int` / `float`** | Whole number / number with decimals | Bilangan bulat / desimal |
| **`str`** | Text | Teks |
| **`bool`** | True or False | Benar atau salah |
| **`None`** | "No value yet" | Belum ada nilai |
| **Type conversion** | Turning one type into another (`int("12")`) | Mengubah jenis nilai |
| **Truthy / falsy** | Values Python treats as true or false in a condition | Dianggap benar / salah |

## 🧠 The big idea

A :term[variable]{bahasa="variabel — nama yang menunjuk ke sebuah nilai yang disimpan program"} is a **name tag** you stick on a value so you can find it later.

```python
price = 450000
```

Python creates the value `450000` in memory and sticks the tag `price` on it. Later, `price` gives you that value back.

A :term[data type]{bahasa="tipe data — jenis nilai (angka, teks, benar/salah) yang menentukan apa yang boleh dilakukan"} says **what kind of value** it is — and therefore what you're allowed to do with it. You can divide numbers. You can make text uppercase. You can't make a number uppercase.

## ❓ Why it matters

Every program stores things: a price, a name, whether the user is logged in. The type decides what you can do with each one — you can divide numbers, you can uppercase text, and you can't uppercase a number.

It matters most at the edges. Data from a form, a file or an API arrives as **text**, always:

```python
age = input("Your age: ")   # "25" — a string, not a number
age + 1                      # 💥 TypeError
```

That one fact explains a large share of beginner errors, and it's why converting types carefully is a habit worth building now.

## 📖 Step by step

### 1. Creating and changing variables

```python
name = "Ismail"      # create
age = 29
age = age + 1        # change: read the old value, compute, re-attach the tag
print(name, age)     # Ismail 30
```

`=` means **assign** ("put this tag on that value"), not "is equal to". Equality is `==` (next lesson).

Naming rules and habits:

| ✅ Good | ❌ Avoid | Why |
|---|---|---|
| `total_price` | `tp`, `x` | Readers shouldn't have to guess |
| `is_logged_in` | `logged` | `is_`/`has_` prefixes make booleans obvious |
| `user_count` | `userCount` | Python style is `snake_case` |
| `MAX_RETRIES = 3` | `max_retries` for constants | UPPER_CASE signals "don't change me" |

### 2. The core types

| Type | Example | Use it for |
|---|---|---|
| `int` | `42`, `-7`, `1_000_000` | Whole numbers: counts, ids, rupiah amounts |
| `float` | `3.14`, `0.5` | Numbers with decimals: ratings, measurements |
| `str` | `"hello"`, `'Jakarta'` | Text |
| `bool` | `True`, `False` | Yes/no facts |
| `None` | `None` | "No value (yet)" |
| `list` | `["a", "b"]` | An ordered collection (Lesson 05) |
| `dict` | `{"name": "Ana", "age": 20}` | Named fields, like a JSON object (Week 1) |

```python
print(type(42))        # <class 'int'>
print(type("42"))      # <class 'str'>
print(type(None))      # <class 'NoneType'>
```

### 3. Strings: the type you'll use most

```python
city = "  jakarta  "
print(city.strip())            # "jakarta"      remove spaces at both ends
print(city.strip().title())    # "Jakarta"
print(len("hello"))            # 5
print("Rp" + " " + "15000")    # "Rp 15000"     joining = concatenation

name = "Ana"
age = 20
print(f"{name} is {age} years old")   # f-string: the cleanest way to build text
```

:::tip[f-strings]
Put an `f` before the quotes and variables inside `{}`. You can even format numbers: `f"{1234567:,}"` → `"1,234,567"`.
:::

### 4. Converting between types

Convert at the **edge** — right where the data arrives — then trust the type everywhere else. Converting again and again deeper in the code is how bugs hide.

| From → To | Code | Result |
|---|---|---|
| text → int | `int("42")` | `42` |
| text → float | `float("3.5")` | `3.5` |
| number → text | `str(42)` | `"42"` |
| anything → bool | `bool("")`, `bool("hi")`, `bool(0)` | `False`, `True`, `False` |

Conversion can **fail**:

```python
int("12abc")    # ValueError: invalid literal for int()
int("3.5")      # ValueError — int() won't parse a decimal string
int(3.9)        # 3  — converting a float drops the decimals (no rounding!)
```

Clean the text first when it comes from users:

```python
raw = " 25 "
age = int(raw.strip())   # 25
```

### 5. "Truthy" and "falsy"

Python treats these as `False` in a yes/no situation: `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`. Everything else counts as `True`. That's why `bool("false")` is `True` — it's a non-empty string!

### 6. The float surprise

`0.1 + 0.2` isn't exactly `0.3` because computers store decimals in binary, the way 1/3 can't be written exactly in decimal. This is why money uses `Decimal`, never `float`.

```python
print(0.1 + 0.2)   # 0.30000000000000004
```

Computers store floats in binary and some decimals can't be represented exactly. For **money**, use whole numbers of the smallest unit (rupiah, or cents) as `int`, or Python's `Decimal`.

### 7. Dynamic typing (and a peek at type hints)

Python lets a variable point to any type, and change later:

```python
value = 10
value = "ten"   # allowed in Python
```

You can *describe* the intended type with **type hints**. Python doesn't enforce them at runtime, but editors and tools use them to catch mistakes early:

```python
age: int = 29
name: str = "Ismail"
```

You'll use type hints everywhere later — FastAPI (Module 3) even uses them to validate API input.

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ Benefit | ❌ Cost |
|---|---|---|
| **Dynamic typing** (Python) | Fast to write and experiment | Type mistakes appear only when the code runs |
| **Static typing** (TypeScript, Java) | Many mistakes caught before running | More to write; slower to prototype |
| Python **+ type hints** | Middle ground: flexible, but tools can check | You must keep hints accurate |
| Money as `float` | Easy | Rounding errors |
| Money as `int` (smallest unit) | Exact | Remember to format for display |

- ✅ Convert **at the boundary**: the moment data enters (form, file, API), turn it into the right type once.
- ✅ Use `None` for "unknown / not set yet" instead of fake values like `-1` or `""`.
- 🚫 Don't use `float` for money.
- 🚫 Don't reuse one variable for different types (`result = 5` then `result = "error"`). It confuses readers and tools.


## ⚠️ Common mistakes

- Forgetting `input()` returns `str` → `"3" * 2 == "33"`.
- `bool("False")` → `True` (non-empty string). Compare text instead: `text.lower() == "true"`.
- `int("3.5")` fails; use `float("3.5")` first if decimals are possible.
- Using `=` when you mean `==`.
- Naming a variable `list`, `str` or `type` — it hides Python's built-in of the same name.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why a sign-up form that asks for your **age** gives the program the text `"29"` and not the number `29`, and what could go wrong if the program forgets to convert it. Maximum 5 sentences.

## 📐 Design it

You're storing a **job listing** for CareerPilot. For each field, choose a type and write one example value:

`title`, `company`, `salary_min`, `salary_max`, `is_remote`, `posted_date`, `application_deadline` (some listings don't have one), `rating` (e.g. 4.3)

:::quiz
Show a possible design

| Field | Type | Example | Why |
|---|---|---|---|
| `title` | `str` | `"Junior Backend Engineer"` | text |
| `company` | `str` | `"Nusantara Tech"` | text |
| `salary_min` | `int` | `9000000` | money as whole rupiah |
| `salary_max` | `int` | `14000000` | same |
| `is_remote` | `bool` | `True` | yes/no |
| `posted_date` | `str` (ISO) for now | `"2026-09-01"` | later: `datetime.date` |
| `application_deadline` | `str` **or `None`** | `None` | missing is a real state |
| `rating` | `float` | `4.3` | decimals, not money |
:::

### 📝 Self-review checklist

- [ ] Money fields are `int`, not `float`
- [ ] Yes/no fields are `bool`, not `"yes"`/`"no"` strings
- [ ] "Might be missing" fields allow `None`
- [ ] My explanation mentions *where* the conversion should happen

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

## 🧸 Clean up form data

:::exercise{path="exercises/m1/w0/02-data-types" ai="no-ai" title="Convert raw form input"}
A sign-up form sends everything as text. In `form_data.py`, complete three functions:

- `parse_age(text)` → `int`, ignoring spaces around the number
- `parse_height_m(text)` → `float` height in meters from centimeters text (`"172"` → `1.72`)
- `parse_newsletter(text)` → `True` only for `"yes"`, `"y"` or `"true"` (any capitalization, spaces allowed)

Then `describe_user(name, age)` returns exactly `"Ana (20 years old)"` using an f-string.

You haven't learned functions yet — that's fine. Write your code where it says `# YOUR CODE HERE` and end with `return`.
:::

:::hints
- `"  25 ".strip()` removes the spaces, then `int(...)` converts.
- 172 cm is 1.72 m — divide by 100.
- Normalize first: `text.strip().lower()`, then compare with `==` or `in ("yes", "y", "true")`.
- An f-string looks like `f"{name} ({age} years old)"`.
:::

### 🏆 Stretch goal

Add `parse_price_idr(text)` that turns `"Rp 15.000"` or `"15000"` into the `int` `15000`. (Hint: `.replace()`.)

## ✅ Quick check

:::quiz
What does `int(7.99)` return, and why might that be a problem in a shop?

`7` — `int()` cuts off the decimals, it doesn't round. Money calculations would silently lose value; use `round()` deliberately or store money as integers.
:::

:::quiz
Why is `bool("0")` equal to `True`?

Because `"0"` is a **non-empty string**. Only empty strings are falsy. Convert the text to a number first if you mean the number zero.
:::

:::quiz
Where is the best place to convert user input into the right types?

At the **boundary** — as soon as the data enters your program (form handler, file reader, API endpoint), so the rest of the code can trust the types.
:::


## 📚 Keep learning

- [Python tutorial: An Informal Introduction](https://docs.python.org/3/tutorial/introduction.html)
- [Python docs: Built-in Types](https://docs.python.org/3/library/stdtypes.html)
