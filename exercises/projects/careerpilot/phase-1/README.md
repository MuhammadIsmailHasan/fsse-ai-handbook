# CareerPilot · Phase 1 Starter Kit

Copy this folder into your own repo as `careerpilot/cli/`.

```text
cli/
├── data/jobs.csv          ← fictional listings (messy on purpose)
├── analyze.py             ← your analysis functions (stubs)
├── cli.py                 ← your command-line entry point (stub)
└── test_acceptance.py     ← acceptance tests — don't edit
```

## Run the tests

In the handbook:

```bash
cd exercises
uv run pytest projects/careerpilot/phase-1
```

In your own repo:

```bash
cd cli
python -m venv .venv && source .venv/bin/activate
pip install pytest
python -m pytest
```

## Run the tool

```bash
python cli.py data/jobs.csv --top 5
python cli.py data/jobs.csv --city jakarta --remote --min-salary 12000000
```

The full brief is in the handbook: **Projects → CareerPilot → Phase 1**.
There's no `solution/` folder for projects — this one is yours. 💪
