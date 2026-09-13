# M2 · W3 · 05 — Skills Gap Engine

> 🚫🤖 **No-AI** · ⏱️ ~50 min

Implement in `skills_gap.py`:

### `JobListing` — `@dataclass(frozen=True, slots=True)`
Fields: `id: int`, `title: str`, `company: str`, `required_skills: frozenset[str]`
- `JobListing.from_dict(data)` (classmethod): skills come as a list of strings; normalize to lowercase, stripped, non-empty, in a `frozenset`.

### Functions
| Function | Returns |
|---|---|
| `match_score(job, my_skills)` | float 0–1: share of required skills I have (`my_skills` may contain any case/spaces); a job requiring nothing scores `1.0` |
| `missing_skills(job, my_skills)` | sorted list of required skills I don't have |
| `missing_skill_demand(jobs, my_skills)` | `Counter`: for each missing skill, how many jobs require it |
| `jobs_by_company(jobs)` | `dict[str, list[JobListing]]` (use `defaultdict`, return a plain `dict`) |
| `best_matches(jobs, my_skills, n)` | top `n` jobs by score desc, then `id` asc |

### `RecentlyViewed(limit)`
- `add(job_id)` — most recent first, no duplicates (re-adding moves it to the front), keeps at most `limit`
- `items()` — list of ids, most recent first

```bash
cd exercises
uv run pytest m2/w3/05-data-structures
```
