"""YOUR tests for discounts.py. Replace this weak starter test with real ones.

Run just your tests:     uv run pytest m2/w6/01-pytest-basics/test_discounts.py -v
Check against mutants:   uv run pytest m2/w6/01-pytest-basics/test_grader.py -v
"""

from discounts import apply_discount


def test_apply_discount_runs():
    # ❌ A weak test: it runs the code but checks almost nothing.
    assert apply_discount(100_000, 10) is not None
