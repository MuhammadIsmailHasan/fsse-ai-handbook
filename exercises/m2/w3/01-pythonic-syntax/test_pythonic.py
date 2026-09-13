"""Behavior + style checks for pythonic.py. Don't edit this file."""

import ast
from pathlib import Path

import pytest

import legacy
import pythonic

SOURCE = Path(__file__).with_name("pythonic.py").read_text()
TREE = ast.parse(SOURCE)

JOBS = [
    {"title": "Backend Dev", "remote": True, "salary": 12},
    {"title": "QA", "remote": False, "salary": 8},
    {"title": "ML Engineer", "remote": True, "salary": None},
    {"title": "SRE", "remote": True, "salary": 20},
]


def test_numbered_titles():
    assert pythonic.numbered_titles(JOBS) == legacy.numbered_titles(JOBS) == ["1. Backend Dev", "2. SRE"]
    assert pythonic.numbered_titles([]) == []


def test_pair_scores():
    assert pythonic.pair_scores(["ana", "budi"], [90, 75]) == {"ana": 90, "budi": 75}
    with pytest.raises(ValueError):
        pythonic.pair_scores(["ana"], [1, 2])


@pytest.mark.parametrize("name", ["ana putri", "  Budi   santoso ", "citra"])
def test_initials(name):
    assert pythonic.initials(name) == legacy.initials(name)


def test_count_lines_with(tmp_path):
    path = tmp_path / "log.txt"
    path.write_text("Python is fun\nI like SQL\npython again ☕\n", encoding="utf-8")
    assert pythonic.count_lines_with(str(path), "PYTHON") == 2


def test_no_range_len():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "range" and node.args:
            first = node.args[0]
            assert not (isinstance(first, ast.Call) and getattr(first.func, "id", None) == "len"), "Avoid range(len(...))"


def test_no_comparisons_to_none_or_bools():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Compare):
            for op, right in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(right, ast.Constant) and right.value in (None, True, False):
                    if isinstance(right.value, bool) or right.value is None:
                        pytest.fail("Use `is None` / truthiness instead of == None / == True")


def test_no_shadowed_builtins():
    shadowed = {"list", "dict", "str", "id", "type", "input", "sum", "max", "min"}
    names = {n.id for n in ast.walk(TREE) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    assert not names & shadowed, f"Don't shadow built-ins: {names & shadowed}"


def test_file_opened_with_context_manager_and_encoding():
    uses_with = any(isinstance(node, ast.With) for node in ast.walk(TREE))
    uses_read_text = "read_text(" in SOURCE
    assert uses_with or uses_read_text, "Open the file with `with open(...)` (or Path.read_text)"
    assert "utf-8" in SOURCE.lower(), "Pass encoding='utf-8'"
