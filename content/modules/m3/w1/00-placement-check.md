---
title: "Week 1 Placement Check"
summary: Do you already know why FastAPI exists, how Pydantic validates data, how path/query/body params work, and where the automatic docs come from? If yes, skim the week.
type: placement-check
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 20
tags: [placement, fastapi, pydantic]
---

::::placement{id="modules/m3/w1"}
You built RevoShop's API with Flask. FastAPI does the same job with types and automatic docs. Can you explain these without looking?

:::quiz
1 · What does FastAPI give you "for free" that plain Flask does not?

Automatic request validation and interactive API docs (Swagger UI / OpenAPI), both generated from your Python **type hints** and Pydantic models — plus first-class `async` support. You declare the shape of your data once, and FastAPI validates inputs and documents the endpoint for you.
:::

:::quiz
2 · What is a Pydantic model, and what happens when data doesn't match it?

A class that describes the expected shape and types of data (fields, types, constraints). When incoming JSON doesn't match, Pydantic raises a validation error and FastAPI returns a `422 Unprocessable Entity` with a clear message saying which field was wrong — you don't write that checking code yourself.
:::

:::quiz
3 · In `@app.get("/items/{item_id}")` with `def read(item_id: int, q: str | None = None)`, which is a path param and which is a query param?

`item_id` is a **path** parameter (it appears in the URL path `/items/{item_id}`), and `q` is a **query** parameter (it's a function argument not in the path, so it comes from the query string like `?q=phone`). FastAPI decides this by matching argument names to the path.
:::

:::quiz
4 · Where does the `/docs` page come from, and why is it useful?

FastAPI generates an OpenAPI schema from your routes and Pydantic models, and serves an interactive Swagger UI at `/docs` automatically. It lets you (and frontend teammates) see every endpoint, its inputs/outputs, and try requests in the browser — no separate documentation to maintain.
:::

:::quiz
5 · You already know Flask. When is reaching for FastAPI worth it, and when is Flask fine?

FastAPI shines when you want automatic validation and docs, type safety, and lots of `async` I/O (many concurrent external calls). Flask is perfectly fine for simpler apps or an existing Flask codebase. Both are solid; FastAPI trades a little more up-front typing for validation and docs you don't have to write.
:::
::::
