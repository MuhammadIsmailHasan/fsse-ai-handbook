# M4 · W1 · 06 — Array Methods on Job Data

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`jobs-data.js`**

Every function takes an array of jobs `{ id, title, company, city, remote, salaryMax, skills }` (`salaryMax` may be `null`). Use array methods — **no `for`/`while` loops** and **never mutate the input** (tests check both).

| Function | Returns |
|---|---|
| `remoteTitles(jobs)` | titles of remote jobs, in order (`filter` + `map`) |
| `averageSalary(jobs)` | average `salaryMax` of jobs that have one, rounded down; `0` if none (`reduce`) |
| `skillCounts(jobs)` | object `{ skill: count }` across all jobs, skills lower-cased (`reduce`) |
| `topPaying(jobs, n)` | the `n` jobs with the highest `salaryMax` (jobs without salary last), ties by `id`; a **new** array (`toSorted` or spread + `sort`) |
| `jobsByCity(jobs)` | object `{ city: [titles…] }` (`Object.groupBy` then map, or `reduce`) |
| `everyHasSalary(jobs)` / `someInCity(jobs, city)` | booleans (`every`, `some`) — city match is case-insensitive |
| `uniqueSkills(jobs)` | sorted, de-duplicated, lower-cased skills (`flatMap` + `Set`) |
| `findById(jobs, id)` | the job or `undefined` (`find`) |

```bash
cd exercises/web
npx vitest run m4/w1/06-array-methods
```
