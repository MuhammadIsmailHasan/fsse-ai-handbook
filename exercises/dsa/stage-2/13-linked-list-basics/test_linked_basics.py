import ast
import random
from pathlib import Path

import pytest

from linked_basics import from_list, has_cycle, middle_node, reverse_list, to_list


def nodes(head):
    result = []
    while head is not None:
        result.append(head)
        head = head.next
    return result


@pytest.mark.parametrize("values", [[1, 2, 3], [], [7], [1, 2], list(range(50))])
def test_reverse_relinks_same_nodes(values):
    head = from_list(values)
    original = nodes(head)
    new_head = reverse_list(head)
    assert to_list(new_head) == values[::-1]
    assert {id(n) for n in nodes(new_head)} == {id(n) for n in original}, "reuse the nodes — don't create new ones"


def test_reverse_long_list_without_recursion_limit():
    assert to_list(reverse_list(from_list(list(range(100_000)))))[:2] == [99_999, 99_998]


@pytest.mark.parametrize(("values", "expected"), [([1, 2, 3], 2), ([1, 2, 3, 4], 3), ([9], 9), ([1, 2], 2)])
def test_middle_node(values, expected):
    head = from_list(values)
    middle = middle_node(head)
    assert middle.val == expected
    assert middle in nodes(head), "return the node itself"


def test_middle_of_empty():
    assert middle_node(None) is None


def make_cycle(values, pos):
    head = from_list(values)
    if pos is not None:
        all_nodes = nodes(head)
        all_nodes[-1].next = all_nodes[pos]
    return head


@pytest.mark.parametrize(("values", "pos", "expected"), [([3, 2, 0, -4], 1, True), ([1, 2], 0, True), ([1], 0, True), ([1], None, False), ([], None, False), ([1, 2, 3], None, False)])
def test_has_cycle(values, pos, expected):
    assert has_cycle(make_cycle(values, pos)) is expected


def test_has_cycle_random():
    rng = random.Random(14)
    for _ in range(200):
        values = list(range(rng.randint(1, 30)))
        pos = rng.choice([None, rng.randrange(len(values))])
        assert has_cycle(make_cycle(values, pos)) is (pos is not None)


def test_has_cycle_uses_constant_memory():
    tree = ast.parse((Path(__file__).parent / "linked_basics.py").read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "has_cycle")
    names = {n.id for n in ast.walk(function) if isinstance(n, ast.Name)}
    assert not names & {"set", "dict", "list"} and not any(isinstance(n, (ast.Set, ast.Dict, ast.List, ast.SetComp, ast.DictComp)) for n in ast.walk(function)), "use two pointers, not a visited set"
