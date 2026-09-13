---
title: "Week 0 Placement Check"
summary: Find out in 20 minutes whether you can skip ahead — answer from memory, no notes, no AI.
type: placement-check
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 20
tags: [placement]
---

You may have met these topics already. This check tells you whether to **study** Week 0 or **skim** it and go straight to the exercises.

::::placement{id="modules/m1/w0"}
Write your answers down (paper or the notes box below) **before** opening each answer.

:::quiz
1 · You type `https://shop.example.com/products?page=2` and press Enter. Name the main steps until the page appears.

(1) The browser asks DNS for the IP address of `shop.example.com`. (2) It connects to that server (with TLS, because of `https`). (3) It sends an HTTP **GET** request for `/products` with the query `page=2`. (4) The server runs code, maybe reads a database, and returns a **response** with a status code (e.g. 200) and a body (HTML or JSON). (5) The browser renders it.
:::

:::quiz
2 · What does this print, and why? `print("5" + 5)`

Nothing — it raises a `TypeError`. You can't add a `str` and an `int` in Python. Convert first: `int("5") + 5` → `10`, or `"5" + str(5)` → `"55"`.
:::

:::quiz
3 · What are the values of `17 // 5`, `17 % 5`, and `True and not False`?

`3` (whole-number division), `2` (remainder), `True`.
:::

:::quiz
4 · Write (on paper) a function `category(code)` that returns `"success"` for HTTP codes 200–299, `"client error"` for 400–499, `"server error"` for 500–599, and `"other"` otherwise.

```python
def category(code: int) -> str:
    if 200 <= code <= 299:
        return "success"
    elif 400 <= code <= 499:
        return "client error"
    elif 500 <= code <= 599:
        return "server error"
    return "other"
```

Check yourself: did you use `elif` (so only one branch runs) and handle "otherwise"?
:::

:::quiz
5 · Write a loop that returns the total of a list of prices, and explain what should happen for an empty list.

```python
def total(prices: list[float]) -> float:
    result = 0
    for price in prices:
        result += price
    return result
```

An empty list returns `0` — the loop body never runs. (Python's built-in `sum(prices)` does the same.)
:::

:::quiz
6 · An error message ends with `IndexError: list index out of range`. What does it mean, and where do you look first?

Your code asked for a position that doesn't exist (e.g. `items[3]` on a list of 3 items — valid positions are 0, 1, 2). Read the traceback **from the bottom up**: the last lines show the exact file and line number that failed.
:::
::::

:::tip[Scoring yourself]
Pass if you got **at least 5 of 6** right *and* could explain *why*, not just *what*. Getting the code right by guessing doesn't count.
:::
