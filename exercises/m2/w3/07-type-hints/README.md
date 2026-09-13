# M2 · W3 · 07 — Type It, Then Let mypy Judge

> 🚫🤖 **No-AI** · ⏱️ ~45 min

`service.py` runs, but has no type hints and **two `None` bugs** that only crash for certain inputs.

1. Add complete type hints to **everything** in `service.py`:
   - `Status` as a `Literal` of `"applied"`, `"interview"`, `"offer"`, `"rejected"`
   - `ApplicationData` as a `TypedDict` with `id: int`, `company: str`, `status: Status`, `salary: int | None`
   - `ApplicationRepository` as a `Protocol` with `get(application_id: int) -> ApplicationData | None` and `save(application: ApplicationData) -> None`
   - a generic `first_or_none` function
2. Run `uv run mypy --strict m2/w3/07-type-hints/service.py` and fix what it finds.
3. Behavior after fixing:
   - `salary_label(repo, id)` → `"Rp 12.000.000"`, or `"Not disclosed"` if salary is `None`; unknown id → raise `LookupError`
   - `advance(repo, id, status)` → saves and returns the updated application; unknown id → `LookupError`

```bash
cd exercises
uv run pytest m2/w3/07-type-hints
```
