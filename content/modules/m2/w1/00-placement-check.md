---
title: "Week 1 Placement Check"
summary: Check your everyday engineering toolkit — terminal, Git, Markdown, virtual environments and Docker — in 20 minutes.
type: placement-check
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 20
tags: [placement]
---

::::placement{id="modules/m2/w1"}
You've probably used these tools in RevoShop. This check asks whether you can **explain** them — not only type the commands.

:::quiz
1 · What's the difference between `git add`, `git commit` and `git push`?

`add` moves changes into the **staging area** (choosing what goes into the next commit). `commit` saves a snapshot of the staged changes in your **local** history with a message. `push` uploads your local commits to a **remote** repository (e.g. GitHub).
:::

:::quiz
2 · A teammate's pull request has a merge conflict in `app/routes/products.py`. What does that mean and how do you resolve it?

Both branches changed the same lines differently, so Git can't choose. Update your branch (`git pull`/`git merge main` or rebase), open the file, keep the correct combination between the `<<<<<<<`, `=======`, `>>>>>>>` markers, remove the markers, run the tests, then `git add` and commit (or continue the rebase).
:::

:::quiz
3 · Why do Python projects use a virtual environment, and what file records the dependencies?

So each project has its own isolated package versions and doesn't break others or the system Python. Dependencies are recorded in `pyproject.toml` (plus a lock file such as `uv.lock`), or in `requirements.txt` in older setups.
:::

:::quiz
4 · In a terminal, how do you find every `.py` file under `app/` that contains the text `jwt_required`?

`grep -rn "jwt_required" app --include="*.py"` (or `rg jwt_required app` with ripgrep).
:::

:::quiz
5 · What's the difference between a Docker **image** and a **container**?

An image is a read-only **template** (the app + its environment, built from a Dockerfile). A container is a **running instance** of an image. One image can run as many containers.
:::

:::quiz
6 · Name three things that must never be committed to Git.

Secrets (`.env`, API keys, passwords, private keys), generated/large folders (`node_modules/`, `.venv/`, `__pycache__/`, build output), and personal/OS files (`.DS_Store`, editor settings) — plus real user data.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6** explained correctly. If you only knew the commands but not *why*, study the week — it's short and pays off daily.
:::
