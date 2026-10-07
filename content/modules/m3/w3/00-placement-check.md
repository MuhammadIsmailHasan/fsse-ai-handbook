---
title: "Week 3 Placement Check"
summary: Can you test a FastAPI app with TestClient, lay out a real project, run work after the response, stream a response, and choose between Flask and FastAPI? If yes, skim the week.
type: placement-check
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 20
tags: [placement, fastapi, testing, project-structure, background-tasks]
---

::::placement{id="modules/m3/w3"}
This week turns a FastAPI demo into a real app. Can you explain these without looking?

:::quiz
1 · How do you test a FastAPI endpoint without starting a server, and how do you swap the real database for a fake one?

Use `TestClient(app)` — it calls the app directly, in the same process, and you assert on `status_code` and `.json()`. To swap a dependency, set `app.dependency_overrides[get_db] = fake_get_db` for the test, and clear it afterward so the next test starts clean.
:::

:::quiz
2 · Why do real FastAPI apps split code into routers, services, schemas and models instead of one `main.py`?

Each file gets one job, so a change stays in one place and each part can be tested alone. Routers handle HTTP, services hold business rules, schemas describe request/response shapes, models describe database tables. One big file mixes all of that and becomes hard to change and test.
:::

:::quiz
3 · What does `BackgroundTasks` do, and when is it the wrong tool?

It runs a function **after** the response is sent, so the client does not wait (for example, sending a welcome email). It is the wrong tool for slow or important work that must survive a crash or restart, because the task lives inside the web process. For that, use a real job queue.
:::

:::quiz
4 · What is a streaming response, and why would an AI endpoint use one?

A streaming response sends the body in small pieces as they are ready, instead of waiting for the whole answer. An AI endpoint streams tokens as the model produces them, so the user sees words appear right away instead of staring at a blank screen.
:::

:::quiz
5 · Give one reason to pick FastAPI over Flask for a new service, and one reason to stay with Flask.

FastAPI: built-in validation, automatic OpenAPI docs and first-class `async`, which suits API-heavy and AI services. Flask: a mature, simple ecosystem and an existing codebase your team already knows — rewriting a working app has a real cost.
:::
::::
