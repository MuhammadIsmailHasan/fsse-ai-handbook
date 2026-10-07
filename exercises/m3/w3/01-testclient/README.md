# Module 3 · W3 · A Test Client With a Fresh Repository

> 🚫🤖 **No-AI** · ⏱️ ~30 min

`notes_app.py` is a finished notes API. It reads notes through a `get_repo` dependency, and in production that is **one shared repository** that lives as long as the process. If tests used it, notes from one test would leak into the next.

Your job, in `notes_testing.py`: write `client_with_fresh_repo(repo=None)`, a context manager that

1. overrides `get_repo` so the app uses a **fresh** `NoteRepo()` (or the `repo` you pass in),
2. yields a `TestClient`,
3. **always** removes the override when the block ends, even if the test body raised an error.

The tests check the API, isolation between tests, a prefilled repository, and the cleanup.

```bash
cd exercises
uv run pytest m3/w3/01-testclient
```
