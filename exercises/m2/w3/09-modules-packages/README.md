# M2 · W3 · 09 — From One File to a Package

> 🚫🤖 **No-AI** · ⏱️ ~40 min

Split `monolith.py` into a package **in this folder**:

```text
careerpilot_core/
├── __init__.py      # exports JobListing, top_skills, format_report; __version__ = "0.1.0"
├── models.py        # JobListing (imports nothing from the package)
├── analysis.py      # top_skills (may import models only)
├── formatting.py    # format_report (may import models and analysis)
└── __main__.py      # CLI (argparse)
```

CLI behavior (run from this folder):

```bash
uv run python -m careerpilot_core --version
# 0.1.0
uv run python -m careerpilot_core report "Backend Dev:python,sql" "AI Engineer:python,llm" --top 2
# Top skills across 2 job(s):
# 1. python (2)
# 2. llm (1)
```

Each job argument is `"Title:skill1,skill2"`. Keep `monolith.py` unchanged (the tests compare behavior with it).

```bash
cd exercises
uv run pytest m2/w3/09-modules-packages
```
