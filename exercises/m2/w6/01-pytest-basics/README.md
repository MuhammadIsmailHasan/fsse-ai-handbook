# M2 · W6 · 01 — Tests That Catch Bugs

> 🚫🤖 **No-AI** · ⏱️ ~60 min · no database needed

`discounts.py` is **correct**. Your job is to write `test_discounts.py`.

The grader (`test_grader.py`) runs your tests:
1. against `discounts.py` → your tests must **pass**
2. against each file in `mutants/` (a copy of `discounts.py` with **one** small bug) → your tests must **fail**

🙈 **Don't open `mutants/` before you're done.** Read the docstrings in `discounts.py`, list the rules, boundaries and error cases, write tests — then let the grader tell you which bugs survived.

```bash
cd exercises
uv run pytest m2/w6/01-pytest-basics/test_discounts.py -v   # your tests on the correct code
uv run pytest m2/w6/01-pytest-basics/test_grader.py -v      # which mutants survive?
```

Rules for good tests here:
- one behavior per test, names that read like requirements
- use `@pytest.mark.parametrize` for boundaries
- use `pytest.raises(ValueError, match=...)` for error cases
- a test that errors (e.g. import error) doesn't count as killing a mutant
