---
title: "Functions: Creating Reusable Blocks of Logic"
summary: Package logic into named, testable functions — parameters, return values, scope, and pure vs side-effect code.
type: lesson
source: core
sourceRef: "M1 · W0 · L5"
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [python, functions, testing, clean-code]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Define functions with **parameters**, **default values** and **return values**
- The difference between `return` and `print`
- **Scope**: which variables a function can see
- **Pure functions** vs functions with **side effects**, and why it matters for testing
- Docstrings and type hints

## 🧠 The big idea

A :term[function]{bahasa="fungsi — blok kode bernama yang menerima input dan menghasilkan output"} is a **recipe card**. It has a name ("Fried Rice"), ingredients you pass in (parameters), steps, and a dish that comes out (the return value). Once written, anyone can cook it again by name — without rereading the steps.

```python
def format_rupiah(amount: int) -> str:
    return f"Rp {amount:,}".replace(",", ".")

print(format_rupiah(1500000))   # Rp 1.500.000
```

## ❓ Why does this exist?

- **Don't repeat yourself**: write the logic once, use it everywhere. Fix a bug once, it's fixed everywhere.
- **Give ideas a name**: `is_valid_email(text)` is easier to read than the 6 lines inside it.
- **Test in isolation**: a function with clear inputs and outputs can be tested alone — you've been doing exactly that in every exercise so far.
- **Divide work**: big programs are built from small functions, like LEGO.

## 💥 What happens if we DON'T use them?

```python
# Checkout page
total = 0
for item in cart:
    total += item["price"] * item["qty"]
if total >= 500_000:
    total = total * 90 // 100

# Invoice email (copy-pasted...)
total2 = 0
for item in cart:
    total2 += item["price"] * item["qty"]
if total2 > 500_000:          # 🐛 someone changed >= to > here only
    total2 = total2 * 90 // 100
```

The two copies drifted apart. The checkout page and the invoice now show **different totals** for the same cart. With one `cart_total(cart)` function, that's impossible.

## 📖 How it works, step by step

### 1. Defining and calling

```python
def greet(name):            # define: parameter `name`
    return f"Hello, {name}!"

message = greet("Ana")      # call: argument "Ana"
print(message)
```

- `def` creates the function. The body is indented.
- :term[Parameters]{bahasa="parameter — nama input di definisi fungsi"} are the names in the definition; **arguments** are the actual values you pass.
- Nothing runs until you **call** it.

### 2. `return` vs `print`

```python
def add_print(a, b):
    print(a + b)       # shows it on screen, gives back None

def add_return(a, b):
    return a + b       # gives the value back to the caller

result = add_print(2, 3)    # prints 5
print(result)               # None 😬

result = add_return(2, 3)
print(result * 10)          # 50 ✅ — we can keep using the value
```

`print` talks to **humans**. `return` talks to **the rest of your program**. Functions that compute something should almost always `return`.

`return` also **ends** the function immediately — that's how guard clauses work.

### 3. Default values and keyword arguments

```python
def apply_discount(price: int, percent: int = 10) -> int:
    return price * (100 - percent) // 100

apply_discount(200_000)               # 180000   (uses default 10)
apply_discount(200_000, 25)           # 150000
apply_discount(price=200_000, percent=25)   # keyword arguments: clearer
```

:::danger[Never use a mutable default]
`def add_item(item, cart=[]):` — that single list is **shared between all calls** and keeps growing. Use `cart=None` and create the list inside: `if cart is None: cart = []`.
:::

### 4. Returning several values

```python
def min_max(values: list[int]) -> tuple[int, int]:
    return min(values), max(values)

low, high = min_max([4, 9, 1])   # "unpacking"
```

### 5. Scope: what a function can see

```python
tax_rate = 11            # global variable

def with_tax(price):
    total = price * (100 + tax_rate) // 100   # can READ the global
    return total

print(with_tax(100))     # 111
print(total)             # ❌ NameError — `total` only exists inside the function
```

Variables created inside a function are **local**: they appear when the function runs and disappear when it returns. That's a feature — functions can't accidentally trample each other's variables.

Relying on globals makes functions harder to test and reuse. Prefer passing values as parameters: `def with_tax(price, tax_rate=11)`.

### 6. Pure functions vs side effects

| Pure function | Function with side effects |
|---|---|
| Output depends **only** on inputs | Reads/changes the outside world |
| Same input → same output, always | Result can vary (time, files, database, network) |
| `cart_total(items)` | `save_order(order)`, `send_email(...)`, `print(...)`, `datetime.now()` |
| Trivial to test | Needs setup, fakes or a real database to test |

Good design: keep **decisions** in pure functions, and push side effects to the edges.

```python
def build_welcome_email(name: str) -> str:     # pure: easy to test
    return f"Hi {name}, welcome to CareerPilot!"

def send_welcome(user):                        # side effect: thin wrapper
    email_service.send(user.email, build_welcome_email(user.name))
```

### 7. Docstrings and type hints

```python
def page_count(total_items: int, per_page: int = 20) -> int:
    """Return how many pages are needed to show all items.

    >>> page_count(45, 20)
    3
    """
    return (total_items + per_page - 1) // per_page
```

Type hints (`: int`, `-> int`) and the docstring tell readers — and editors — how to use the function without reading its body.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Many small functions | Readable, testable, reusable | Jumping between functions while reading |
| One big function | Everything in one place | Hard to test and change safely |
| Pure functions | Predictable, easy tests | Something still has to do the side effects |
| Globals | Quick to write | Hidden dependencies, surprising bugs |
| Default parameters | Convenient API | Too many options make functions confusing |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Extract a function when you copy code a **second** time, or when a block deserves a **name**.
- ✅ Aim for functions that do **one thing** (if the name needs "and", consider splitting).
- 🚫 Don't create a function for a single obvious line used once (`def add_one(x): return x + 1`).
- 🚫 Don't hide side effects in functions whose names sound pure (`get_total()` that also saves to the database).

## 🏭 How it's used in industry

- Every API endpoint is a function that receives a request and returns a response.
- Code review comments like *"extract this into a function"* and *"this function does too much"* are among the most common.
- Business rules live in pure "service" functions with hundreds of unit tests; database and email code stays thin. (You'll see this **layered architecture** in Module 2 — and in your RevoShop project.)

## ⚠️ Common mistakes

- Using `print` instead of `return`, then getting `None`.
- Forgetting to **call** the function (`total = cart_total` instead of `cart_total(items)`).
- Mutable default arguments.
- Functions that silently change their input list (surprise!). Return a new list, or name it clearly (`sort_in_place`).
- Too many parameters (more than ~4 is a hint to group them).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the difference between `return` and `print` to someone who has only ever used a calculator. Then explain in two sentences why pure functions are easier to test.

## 📐 Design it

A teammate wrote one 60-line function `process_order(order)` that: validates the order, calculates the subtotal, applies a voucher, adds shipping, saves the order to the database, and emails the customer.

Split it into smaller functions. For each, write the **name**, **parameters**, **return type**, and mark it **pure** or **side effect**.

:::quiz
Show a possible design

| Function | Returns | Kind |
|---|---|---|
| `validate_order(order) -> list[str]` | list of error messages (empty = valid) | pure |
| `subtotal(items) -> int` | rupiah | pure |
| `apply_voucher(amount, voucher) -> int` | rupiah after discount | pure |
| `shipping_fee(weight_kg, express) -> int` | rupiah | pure |
| `order_total(order) -> int` | combines the three above | pure |
| `save_order(order, total) -> int` | new order id | side effect |
| `send_confirmation(email, order_id, total) -> None` | — | side effect |
| `process_order(order)` | coordinates everything, short | side effect |

Five of eight are pure → most of the logic can be tested without a database or email server.
:::

### 📝 Self-review checklist

- [ ] Each function does one thing and its name says what
- [ ] Calculations are pure; database/email work is separate
- [ ] No function has more than ~4 parameters
- [ ] I could write a test for each pure function without any setup

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

## 🧸 Refactor into functions

:::exercise{path="exercises/m1/w0/06-functions" ai="no-ai" title="From copy-paste to functions"}
`pricing.py` contains one messy script with duplicated logic. Rebuild it as functions:

- `format_rupiah(amount)` → `"Rp 1.500.000"`
- `apply_discount(price, percent=10)` → discounted whole-rupiah price (round **down**)
- `line_total(price, qty)` → price × quantity
- `cart_total(items)` → sum of `line_total` for every item (`items` is a list of `(price, qty)` tuples)
- `receipt(items, discount_percent=0)` → a multi-line string (format in the README)

`receipt` must **reuse** your other functions — the tests check the output, your reviewer (you!) checks the reuse.
:::

:::hints
- `f"{1500000:,}"` gives `"1,500,000"`. Replace the commas with dots.
- Rounding down with integers: `price * (100 - percent) // 100`.
- Loop over tuples with unpacking: `for price, qty in items:`.
- Build `receipt` as a list of lines, then `"\n".join(lines)`.
:::

### 🏆 Stretch goal

Make `apply_discount` raise `ValueError` for a percent below 0 or above 100, and add a docstring with an example to every function.

## ✅ Quick check

:::quiz
What does a function return if it has no `return` statement?

`None`.
:::

:::quiz
Why is `def add_tag(tag, tags=[])` dangerous?

The default list is created **once** and shared across calls, so tags from earlier calls leak into later ones. Use `tags=None` and create a new list inside.
:::

:::quiz
Is `def total_with_tax(price): return price * (100 + TAX) // 100` pure if `TAX` is a global constant that never changes?

Practically yes — same input always gives the same output. It becomes impure (and harder to test) if `TAX` can change at runtime. Passing it as a parameter makes the dependency explicit.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Parameter / Argument | Parameter (nama input) / Argumen (nilai yang dikirim) |
| Return value | Nilai kembalian |
| Scope | Cakupan — di mana variabel bisa diakses |
| Pure function | Fungsi murni — hasil hanya bergantung pada input |
| Side effect | Efek samping — mengubah sesuatu di luar fungsi |
| Refactor | Merapikan struktur kode tanpa mengubah perilakunya |

## 📚 Keep learning

- [Python tutorial: Defining functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- [Python tutorial: More on defining functions](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions)
