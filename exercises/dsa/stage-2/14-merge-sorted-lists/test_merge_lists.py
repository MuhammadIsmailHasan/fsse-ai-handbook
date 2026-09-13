import random

import pytest

from merge_lists import from_list, merge_sorted, to_list


def nodes(head):
    result = []
    while head is not None:
        result.append(head)
        head = head.next
    return result


@pytest.mark.parametrize(
    ("a", "b"),
    [([1, 3, 5], [2, 3, 6]), ([], [4, 7]), ([4, 7], []), ([], []), ([1, 1], [1]), ([5, 6], [1, 2])],
)
def test_examples(a, b):
    assert to_list(merge_sorted(from_list(a), from_list(b))) == sorted(a + b)


def test_relinks_nodes_and_is_stable():
    rng = random.Random(15)
    for _ in range(200):
        a = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 8)))
        b = sorted(rng.randint(0, 5) for _ in range(rng.randint(0, 8)))
        head_a, head_b = from_list(a), from_list(b)
        origin = {id(n): "a" for n in nodes(head_a)} | {id(n): "b" for n in nodes(head_b)}
        merged = nodes(merge_sorted(head_a, head_b))
        assert [n.val for n in merged] == sorted(a + b)
        assert all(id(n) in origin for n in merged) and len(merged) == len(origin), "reuse the input nodes"
        for left, right in zip(merged, merged[1:]):
            if left.val == right.val and origin[id(left)] == "b":
                assert origin[id(right)] == "b", "equal values: nodes from a come first"


def test_long_lists():
    merged = merge_sorted(from_list(list(range(0, 200_000, 2))), from_list(list(range(1, 200_000, 2))))
    assert to_list(merged)[:5] == [0, 1, 2, 3, 4]
