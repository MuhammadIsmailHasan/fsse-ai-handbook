# Architecture · D · Creational Patterns: Factory, Builder, and a Better Singleton

> 🚫🤖 **No-AI** · ⏱️ ~60 min

Everything goes in **`creational.py`**.

## 1. Factory with a registry
| Piece | Contract |
|---|---|
| `register_exporter(name)` | class decorator: stores the class under `name` in `EXPORTERS` and returns the class unchanged; registering a name twice → `ValueError` |
| `create_exporter(name, **options)` | returns `EXPORTERS[name](**options)`; unknown name → `ValueError("unknown exporter 'xlsx' (available: csv, json)")` with names sorted |
| `CsvLinesExporter` (`"csv"`) | `render(rows) -> str`: each row's values joined by `self.separator` (default `","`), lines joined with `"\n"` |
| `JsonLinesExporter` (`"json"`) | `render(rows) -> str`: one `json.dumps(row)` per line |

## 2. Builder
`JobPosting` is a **frozen** dataclass: `title`, `company`, `city` (`str | None`), `remote` (`bool`), `salary_min`, `salary_max` (`int | None`), `skills` (`tuple[str, ...]`).

`JobPostingBuilder()` — every method returns the builder, so calls chain:
`.titled(title)`, `.at(company)`, `.in_city(city)`, `.remote()`, `.salary(minimum, maximum)`, `.requires(*skills)` (adds skills: trimmed, lower-case, duplicates ignored, order kept).

`.build()` validates and returns a `JobPosting`:
- missing title/company → `ValueError("missing: company, title")` (only the missing ones, sorted)
- neither a city nor remote → `ValueError("city or remote required")`
- `salary_min > salary_max` → `ValueError("salary_min must be <= salary_max")`
- building twice gives two equal postings; later builder changes don't affect postings already built

## 3. Singleton — done safely
| Piece | Contract |
|---|---|
| `Settings` | frozen dataclass `app_env: str`, `database_url: str` |
| `load_settings(env)` | pure: `APP_ENV` (default `"development"`), `DATABASE_URL` (required → `ValueError`) |
| `get_settings()` | returns `load_settings(os.environ)`, **cached** with `functools.cache` (so tests can call `get_settings.cache_clear()`) |

No settings object may be created at import time (a test checks the module's top level).

```bash
cd exercises
uv run pytest architecture/d-design-patterns/01-creational
```
