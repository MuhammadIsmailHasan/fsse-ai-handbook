import ast
import random
import time
from pathlib import Path

import pytest

from priorities import sort_priorities

ORDER = {"high": 0, "medium": 1, "low": 2}


@pytest.mark.parametrize(
    "tasks",
    [["low", "high", "medium", "high", "low"], [], ["low"], ["low", "low", "high"], ["medium", "medium"], ["high", "medium", "low"], ["low", "medium", "high"]],
)
def test_examples(tasks):
    expected = sorted(tasks, key=ORDER.get)
    same = tasks
    assert sort_priorities(tasks) is None
    assert same is tasks and tasks == expected


def test_random():
    rng = random.Random(77)
    for _ in range(500):
        tasks = [rng.choice(list(ORDER)) for _ in range(rng.randint(0, 15))]
        expected = sorted(tasks, key=ORDER.get)
        sort_priorities(tasks)
        assert tasks == expected


def test_one_pass_and_no_shortcuts():
    tree = ast.parse((Path(__file__).parent / "priorities.py").read_text())
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not names & {"sorted", "sort", "Counter", "count"}, "use the Dutch national flag pointers"
    assert not any(isinstance(n, (ast.List, ast.ListComp)) for n in ast.walk(tree)), "don't build a new list"
    tasks = ["low", "medium", "high"] * 100_000
    started = time.perf_counter()
    sort_priorities(tasks)
    assert time.perf_counter() - started < 1.0 and tasks[0] == "high" and tasks[-1] == "low"
