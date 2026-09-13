"""Automatic checks. Don't edit — make them pass by editing counting.py."""

import ast
from pathlib import Path

from counting import count_items, count_skills, first_duplicate, most_frequent, top_skills

LISTINGS = [
    "Python, SQL, Docker",
    "python , React",
    "",
    "SQL, python, AWS",
    "react, TypeScript",
]


def test_count_items():
    assert count_items(["a", "b", "a"]) == {"a": 2, "b": 1}
    assert count_items([]) == {}


def test_most_frequent_with_ties_sorted():
    assert most_frequent(["b", "a", "b", "a", "c"]) == ["a", "b"]
    assert most_frequent(["solo"]) == ["solo"]
    assert most_frequent([]) == []


def test_first_duplicate():
    assert first_duplicate(["x", "y", "z", "y", "x"]) == "y"
    assert first_duplicate(["a", "b", "c"]) is None
    assert first_duplicate([]) is None


def test_count_skills_normalizes_and_skips_empty():
    assert count_skills(LISTINGS) == {
        "python": 3,
        "sql": 2,
        "docker": 1,
        "react": 2,
        "aws": 1,
        "typescript": 1,
    }


def test_top_skills_orders_by_count_then_name():
    assert top_skills(LISTINGS, 3) == [("python", 3), ("react", 2), ("sql", 2)]
    assert top_skills(LISTINGS, 100)[-1] == ("typescript", 1)
    assert top_skills([], 5) == []


def test_does_not_use_counter():
    source = Path(__file__).with_name("counting.py").read_text()
    names = {n.id for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Name)}
    assert "Counter" not in names, "Build it with a plain dict this time!"
