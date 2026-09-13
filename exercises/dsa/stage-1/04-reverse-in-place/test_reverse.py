import ast
from pathlib import Path

import pytest

from reverse import reverse_in_place


@pytest.mark.parametrize(
    ("items", "expected"),
    [([1, 2, 3, 4], [4, 3, 2, 1]), ([1, 2, 3], [3, 2, 1]), ([7], [7]), ([], []), (["a", "b"], ["b", "a"])],
)
def test_reverses_same_list(items, expected):
    same = items
    assert reverse_in_place(items) is None
    assert same == expected


def test_no_shortcuts():
    tree = ast.parse(Path(__file__).with_name("reverse.py").read_text())
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "reversed" not in names and "reverse" not in attrs
    assert not any(isinstance(n, ast.Slice) for n in ast.walk(tree)), "No slicing"
    assert not any(isinstance(n, (ast.List, ast.ListComp)) for n in ast.walk(tree)), "No new lists"
