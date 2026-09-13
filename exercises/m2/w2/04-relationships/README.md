# M2 · W2 · 04 — Relationships & ON DELETE Rules

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

`base.sql` (provided) creates `users` and `companies`. Write `relationships.sql` to add:

### `applications` — many per user, many per company
- `id` bigint identity PK · `user_id` required · `company_id` required · `role_title` text required · `created_at` timestamptz default now
- Deleting a **user** deletes their applications (**cascade**)
- Deleting a **company** that still has applications must **fail** (**restrict**)

### `skills`
- `id` bigint identity PK · `name` text required, unique

### `application_skills` — many-to-many between applications and skills
- `application_id`, `skill_id` — together the **primary key** (no duplicates)
- `level` text required, one of `nice_to_have`, `required`
- Deleting an application removes its links (cascade); deleting a skill that is still linked must fail (restrict)

### `interviews` — many per application
- `id` bigint identity PK · `application_id` required · `scheduled_at` timestamptz required
- Deleting an application deletes its interviews (cascade)

### `user_profiles` — exactly zero or one per user (one-to-one)
- `user_id` is the **primary key** and references `users` · `headline` text · `linkedin_url` text
- Deleting a user deletes the profile (cascade)

### Indexes
Create an index on **every foreign key column that isn't already the first column of a primary key**.

```bash
cd exercises
uv run pytest m2/w2/04-relationships
```
