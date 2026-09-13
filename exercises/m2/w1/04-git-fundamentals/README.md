# M2 · W1 · 04 — Build a Clean Practice History

> 🚫🤖 **No-AI** · ⏱️ ~45 min

Create a Git repo in `practice/` (inside this folder) and follow the story. Use **Conventional Commits** (`type(scope): summary`, types: feat, fix, docs, test, refactor, chore, style). Git's own `Revert "…"` messages are allowed.

```bash
cd exercises/m2/w1/04-git-fundamentals
mkdir practice && cd practice
git init -b main
```

## The story

1. Create `.gitignore` that ignores `.env` and `__pycache__/`. Commit it.
2. Create `app.py` with a `greet(name)` function. Commit.
3. Create a `.env` file with `API_KEY=dev-123`. Make sure it is **not** committed.
4. Create a branch named `feature/<something>`; add a `farewell(name)` function and a `README.md` in **two separate commits**; merge it into `main`.
5. Make a commit that adds a silly line to `README.md`… then undo it with `git revert`.
6. Tag the final `main` commit as `v0.1.0` (annotated tag: `git tag -a v0.1.0 -m "…"`).

## Check

```bash
cd exercises
uv run pytest m2/w1/04-git-fundamentals
```

The tests read your history. If a commit message is wrong and it's the last commit, use `git commit --amend`. For older commits, it's fine to start the practice repo again: `rm -rf practice`.
