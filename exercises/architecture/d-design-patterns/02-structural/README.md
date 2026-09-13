# Architecture · D · Structural Patterns: Adapter, Decorator, Proxy, Facade

> 🚫🤖 **No-AI** · ⏱️ ~75 min

CareerPilot collects jobs from several boards. Provided in `job_sources.py`: the `Job` dataclass, the `JobSource` protocol (`fetch() -> list[Job]`), and `LegacyKarirFeed`, a third-party client with its own format. Implement:

| Pattern | Class | Contract |
|---|---|---|
| **Adapter** | `KarirFeedAdapter(feed)` | `fetch()` converts `feed.get_listings()` dicts: `Job(id=f"karir-{lowongan_id}", title=posisi.strip(), company=perusahaan.strip(), salary_max=...)` where `gaji` like `"Rp 12.000.000"` → `12000000` and anything else (`"Negotiable"`, `""`) → `None` |
| **Decorator** | `CachedSource(inner, ttl_seconds, clock)` | returns the inner result again while `clock() - fetched_at < ttl_seconds`; afterwards fetches again. Returns a **copy** of the list each time |
| **Decorator** | `RetryingSource(inner, attempts=3)` | calls `inner.fetch()` up to `attempts` times on `ConnectionError`; re-raises the last error; other exceptions are not retried |
| **Proxy** | `SalaryPrivacyProxy(inner, can_view_salaries)` | same jobs, but with `salary_max=None` when `can_view_salaries` is `False` (use `dataclasses.replace`) |
| **Facade** | `JobBoards(sources: dict[str, JobSource])` → `refresh()` | fetches every source; returns `RefreshResult(jobs, counts, failed)`: `jobs` unique by `id` (first one wins, source order), `counts[name]` = jobs fetched from that source, `failed` = sorted names of sources that raised any `Exception` (they don't stop the others) |

Every wrapper must itself satisfy `JobSource`, so wrappers can be stacked: `CachedSource(RetryingSource(KarirFeedAdapter(feed)), ...)`.

```bash
cd exercises
uv run pytest architecture/d-design-patterns/02-structural
```
