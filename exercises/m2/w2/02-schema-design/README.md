# M2 · W2 · 02 — CareerPilot Core Schema

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

Write `schema.sql` with three tables.

### `users`
| Column | Rules |
|---|---|
| `id` | bigint identity primary key |
| `email` | required; **unique ignoring case** (`Ana@Mail.com` and `ana@mail.com` are the same) |
| `full_name` | required |
| `created_at` | `timestamptz`, required, default now |

### `companies`
| Column | Rules |
|---|---|
| `id` | bigint identity primary key |
| `name` | required, unique |
| `website` | optional |
| `created_at` | `timestamptz`, required, default now |

### `applications`
| Column | Rules |
|---|---|
| `id` | bigint identity primary key |
| `user_id` | required, references `users` |
| `company_id` | required, references `companies` |
| `role_title` | required, not blank (spaces only is invalid) |
| `status` | required, default `'applied'`, one of `wishlist, applied, interview, offer, rejected, withdrawn` |
| `applied_on` | `date`, optional |
| `salary_expectation` | `bigint`, optional, must be ≥ 0 |
| `notes` | optional |
| `created_at`, `updated_at` | `timestamptz`, required, default now |

A user can't have two applications for the **same company and role title**.

```bash
cd exercises
uv run pytest m2/w2/02-schema-design
```
