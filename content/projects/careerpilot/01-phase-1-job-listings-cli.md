---
title: "Phase 1: Job Listings Analyzer CLI"
summary: Build a tested Python command-line tool that cleans job listing data and reports top skills, salary stats and city breakdowns.
type: project
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 600
tags: [project, careerpilot, python, cli, phase-1]
---

## 🎯 Goal

Build `careerpilot`'s first piece: a **command-line tool** that reads a CSV of job listings and answers the questions every job seeker has:

> *Which skills are most in demand? What do these roles pay? Where are the jobs? What's out there for me?*

```text
$ python cli.py data/jobs.csv --city Jakarta --top 3

CareerPilot · Job Market Report
Jobs analyzed: 13

Top skills:
  1. python (8)
  2. sql (5)
  3. aws (3)

Salary (IDR/month, jobs with salary data: 12):
  Average range: 11.875.000 – 18.208.333
  Median max: 19.000.000

Jobs per city:
  Jakarta: 13
```

## 👤 User stories

1. As a job seeker, I want to see the **top N skills** across listings, so I know what to learn next.
2. As a job seeker, I want **salary statistics**, so I know what to ask for.
3. As a job seeker, I want to **filter** by city, remote, and minimum salary, so the report matches my situation.
4. As a job seeker, I want the tool to **handle messy data** (extra spaces, mixed case, missing salaries) without crashing.

## 📦 Starter kit

:::exercise{path="exercises/projects/careerpilot/phase-1" ai="no-ai" title="Phase 1 starter kit"}
The kit contains **fictional** job data (`data/jobs.csv`), function stubs in `analyze.py` and `cli.py`, and **acceptance tests**.

1. Create your `careerpilot` repository and a `cli/` folder.
2. Copy the kit's contents into `cli/`.
3. Make the acceptance tests pass — then keep going with the stretch goals.

You can run the tests inside the handbook folder too (command below), but the real project lives in **your** repo.
:::

## 📋 Requirements

### Data (`data/jobs.csv`)

Columns: `id, title, company, city, remote, salary_min, salary_max, skills, posted_on`

Cleaning rules for `load_jobs(path)`:

| Field | Rule |
|---|---|
| `title` | trimmed; rows **without a title are skipped** |
| `city` | trimmed, Title Case (`" jakarta"` → `"Jakarta"`) |
| `remote` | `True` for `yes`/`true`/`1` (any case), else `False` |
| `salary_min`, `salary_max` | `int`, or `None` when empty |
| `skills` | list of lowercase trimmed skills, **duplicates removed**, original order kept, empty items dropped |
| `posted_on` | `datetime.date`, or `None` when empty |

### Analysis functions (`analyze.py`)

| Function | Returns |
|---|---|
| `filter_jobs(jobs, city=None, remote=None, min_salary=None)` | jobs matching **all** given filters; `city` case-insensitive; `min_salary` compares with `salary_max` and excludes jobs without salary |
| `top_skills(jobs, n)` | `[(skill, count)]` by count desc, then skill A→Z |
| `salary_stats(jobs)` | `{"count", "average_min", "average_max", "median_max"}` over jobs that have **both** salaries; averages rounded down; median of `salary_max` (average of the two middle values, rounded down, when even); all `0` when there's no data |
| `jobs_by_city(jobs)` | `{city: count}` sorted by count desc, then city A→Z |
| `format_rupiah_number(amount)` | `18208333` → `"18.208.333"` |
| `format_report(jobs, top_n=5)` | the report text shown above. With no salary data, the salary block is the single line `Salary: No salary data` |

### CLI (`cli.py`)

```text
python cli.py PATH [--city CITY] [--remote] [--min-salary AMOUNT] [--top N]
```

- Uses `argparse`
- Missing file → prints `Error: file not found: PATH` to **stderr** and exits with code `1`
- Filters apply before the report

## 🧭 Checkpoints

| # | Checkpoint | Done when |
|---|---|---|
| **C1** | Load & clean | `load_jobs` tests pass; you handled every messy row in the CSV |
| **C2** | Analyze | `filter_jobs`, `top_skills`, `salary_stats`, `jobs_by_city` tests pass |
| **C3** | Report & CLI | `format_report` and CLI tests pass; you ran it on the real file |
| **C4** | Portfolio-ready | README, screenshot of terminal output, `git tag phase-1`, LinkedIn post |

After each checkpoint: commit, and write 3 lines in your notes — *what I built, what was hard, what I learned*.

## 🧪 Acceptance criteria

- [ ] All tests in `test_acceptance.py` pass
- [ ] Functions are small and named clearly (Architecture Stage A!)
- [ ] Business logic (`analyze.py`) has **no** `print` and no file reading except `load_jobs`
- [ ] The CLI only parses arguments, calls functions, and prints
- [ ] README explains install, run, test, and shows sample output

## 🏆 Stretch goals

1. `--json` flag that prints the report data as JSON (hint: `json.dumps`).
2. `--skills python,sql` filter: jobs that require **all** listed skills.
3. Add your own real listings to a second CSV (anonymize companies if you like) and compare markets.
4. `skill_pairs(jobs, n)`: the most common **pairs** of skills (e.g. `python + sql`). Think about the complexity!
5. Add GitHub Actions to run tests on every push (preview of Module 5).

## ❓ Questions an interviewer might ask about Phase 1

- Why did you separate `analyze.py` from `cli.py`?
- How do you handle a CSV with 10 million rows? (Hint: streaming, not loading everything.)
- What's the complexity of `top_skills`? How would you get the top 5 without sorting everything?
- How did you test the CLI?

Write your answers in **My notes** — you'll reuse them in Module 8.

## 📣 Share it

:::linkedin{type="build"}
🚀 Built the first piece of my portfolio project: CareerPilot, a CLI that analyzes job listings.

It reads a CSV of listings and reports:
📊 the most in-demand skills
💰 salary ranges and median
📍 jobs per city — with filters for city, remote and minimum salary

Technical decisions I'm happy with:
- Business logic separated from the CLI, so it's fully unit-tested
- Cleaning messy data (mixed case, missing salaries, duplicate skills) at the boundary

Biggest challenge: [your answer]. Next: turning it into a REST API with Flask and PostgreSQL.

Repo: [link] · [screenshot of the terminal output]

#Python #LearningInPublic #BuildInPublic #SoftwareEngineering
:::
