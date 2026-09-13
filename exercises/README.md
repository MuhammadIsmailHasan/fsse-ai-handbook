# Exercises

Hands-on exercises for the handbook. Each lesson's **🧸 Toy exercise** card tells you which folder to open.

## One-time setup

You need **Python 3.11+**. We recommend [uv](https://docs.astral.sh/uv/) (fast, handles the virtual environment for you).

```bash
cd exercises
uv sync
```

<details>
<summary>No uv? Use pip instead</summary>

```bash
cd exercises
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install pytest
```

Then replace `uv run pytest` with `python -m pytest` in every command.
</details>

## Doing an exercise

```bash
cd exercises
uv run pytest _example/01-word-count     # run the checks (they fail at first — that's expected)
```

1. Read the folder's `README.md`.
2. Edit the Python file (e.g. `word_count.py`). **Don't edit the test file.**
3. Run the checks again. Repeat until everything passes ✅.
4. Stuck? Use the hints in the lesson. Open `solution/` **only after a real attempt**.

## Folder layout

```
exercises/
├── pyproject.toml
├── _example/01-word-count/     ← a sample showing the structure
│   ├── README.md               ← the task
│   ├── word_count.py           ← you edit this
│   ├── test_word_count.py      ← automatic checks
│   └── solution/word_count.py  ← reference solution
├── m1/w0/…                     ← Module 1, Week 0
└── dsa/stage-1/…               ← DSA track
```

## AI policy

- **🚫🤖 No-AI** exercises: solve them yourself. Afterwards, you may ask AI to review your code.
- **🤖✅ AI-allowed** exercises: use AI if you like, but you must be able to explain every line.

## Ports

Exercises that start a server read their port from the project's `.env` (see `.env.example`):
Flask `5091`, FastAPI `8091`, Next.js `3091`, PostgreSQL `5491`, Redis `6391`.
