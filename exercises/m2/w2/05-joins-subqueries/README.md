# M2 · W2 · 05 — JOINs & Subqueries

> 🚫🤖 **No-AI** · ⏱️ ~75 min · needs the exercise database (`docker compose up -d`)

Tables: `users`, `companies`, `applications`, `skills`, `application_skills` (see `seed.sql`). One statement per file; columns and order must match exactly.

| File | Task |
|---|---|
| `q01_applications_with_names.sql` | `full_name, company, role_title` for every application, ordered by `full_name`, then `company` |
| `q02_users_without_applications.sql` | `full_name` of users with **no** applications |
| `q03_company_application_counts.sql` | `company, applications` — **every** company with its number of applications (0 included), most first, then `company` A→Z |
| `q04_offers_above_average.sql` | `full_name, company, salary_offer` of offers whose `salary_offer` is **above the average offer**, highest first |
| `q05_skills_for_ana.sql` | `skill` — distinct skills across all of **Ana Putri**'s applications, A→Z |
| `q06_skill_demand.sql` | `skill, applications` — how many applications require each skill, **including skills used by none**, most first, then `skill` A→Z |
| `q07_users_with_offer.sql` | `full_name` of users who have **at least one offer**, A→Z — use `EXISTS` |
| `q08_latest_application_per_user.sql` | `full_name, role_title, applied_on` — each user's **most recent** application (users with applications only), ordered by `full_name` |
| `q09_same_company_applicants.sql` | `company, user_a, user_b` — pairs of **different** users who applied to the same company, each pair once (`user_a` < `user_b` alphabetically), ordered by `company, user_a, user_b` |
| `q10_status_summary_cte.sql` | `full_name, total, active, offers` — per user with applications: total applications, **active** (`applied` or `interview`), offers; use a CTE (`WITH`); ordered by `offers` desc, then `full_name` |

```bash
cd exercises
uv run pytest m2/w2/05-joins-subqueries
```
