---
title: "Week 3 Placement Check"
summary: Module 1 taught Python basics. This check tests the professional layer — idioms, decorators, classes, type hints, exceptions and packaging.
type: placement-check
source: original
roles: { be: core, fe: optional, fs: core, ai: core, ops: recommended }
durationMinutes: 25
tags: [placement, python]
---

::::placement{id="modules/m2/w3"}
Answer from memory. These are the Python questions backend interviews and code reviews actually ask.

:::quiz
1 · What's the difference between `is` and `==`, and what's wrong with `def add(item, items=[])`?

`==` compares values; `is` compares identity (same object) and should be used for `None`. The default list is created once and **shared across calls**, so items accumulate between calls — use `items=None` and create the list inside.
:::

:::quiz
2 · Write a decorator `timed` that prints how long a function took, and keeps the original function's name.

```python
import functools, time

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
    return wrapper
```
:::

:::quiz
3 · When would you use a `set`, a `dict`, a `tuple` and a `list`?

`list`: ordered, changeable sequence. `tuple`: fixed-size, immutable record (and usable as a dict key). `set`: unique items with fast membership checks. `dict`: key → value lookups.
:::

:::quiz
4 · What does `@dataclass` generate, and when is composition better than inheritance?

It generates `__init__`, `__repr__` and `__eq__` (and optionally ordering/frozen behavior) from annotated fields. Composition ("has-a") is better when you want to combine behaviors without a rigid "is-a" hierarchy — e.g. a service that *has* a notifier instead of *being* a notifier subclass.
:::

:::quiz
5 · What's wrong with this, and how do you fix it?
```python
try:
    user = repo.get(user_id)
except:
    pass
```

A bare `except` catches everything (including `KeyboardInterrupt`) and silently hides bugs; `user` may not even exist afterwards. Catch the **specific** exception you expect (e.g. `UserNotFound`), handle it meaningfully (return 404, log), and let unexpected errors propagate.
:::

:::quiz
6 · What does `if __name__ == "__main__":` do, and why do circular imports happen?

The block runs only when the file is executed directly, not when imported. Circular imports happen when module A imports B at load time while B imports A — usually a sign that shared code should move into a third module (or that responsibilities are tangled).
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. If decorators (Q2) felt shaky, study lesson 04 anyway — Flask is built on them.
:::
