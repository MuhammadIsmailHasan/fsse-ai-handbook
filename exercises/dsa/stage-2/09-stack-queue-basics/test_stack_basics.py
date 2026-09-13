import random
import time

import pytest

from stack_basics import MinStack, apply_backspaces, is_balanced


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("fn(a[i]) { return {x: 1}; }", True),
        ("", True),
        ("no brackets", True),
        ("(]", False),
        ("([)]", False),
        ("((", False),
        ("))((", False),
        ("{[()()]}", True),
    ],
)
def test_is_balanced(text, expected):
    assert is_balanced(text) is expected


def brute_balanced(text):
    text = "".join(c for c in text if c in "()[]{}")
    while any(pair in text for pair in ("()", "[]", "{}")):
        for pair in ("()", "[]", "{}"):
            text = text.replace(pair, "")
    return text == ""


def test_is_balanced_matches_brute_force():
    rng = random.Random(8)
    for _ in range(500):
        text = "".join(rng.choice("()[]{}a") for _ in range(rng.randint(0, 10)))
        assert is_balanced(text) is brute_balanced(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("ab#c##d", "d"), ("###", ""), ("abc", "abc"), ("a##b", "b"), ("", ""), ("xy#z", "xz")],
)
def test_apply_backspaces(text, expected):
    assert apply_backspaces(text) == expected


def test_backspaces_linear():
    text = "ab#" * 200_000
    started = time.perf_counter()
    assert apply_backspaces(text) == "a" * 200_000
    assert time.perf_counter() - started < 0.5, "string slicing on every # is O(n²) — use a list as a stack"


def test_min_stack():
    stack = MinStack()
    stack.push(5)
    stack.push(2)
    stack.push(7)
    stack.push(2)
    assert (stack.top(), stack.get_min()) == (2, 2)
    assert stack.pop() == 2 and stack.get_min() == 2
    assert stack.pop() == 7 and stack.get_min() == 2
    assert stack.pop() == 2 and stack.get_min() == 5
    assert stack.pop() == 5
    for method in (stack.pop, stack.top, stack.get_min):
        with pytest.raises(IndexError):
            method()


def test_min_stack_matches_reference_and_is_constant_time():
    rng = random.Random(2)
    stack, reference = MinStack(), []
    for _ in range(2_000):
        if reference and rng.random() < 0.4:
            assert stack.pop() == reference.pop()
        else:
            value = rng.randint(-50, 50)
            stack.push(value)
            reference.append(value)
        if reference:
            assert stack.get_min() == min(reference) and stack.top() == reference[-1]
    big = MinStack()
    for i in range(100_000, 0, -1):
        big.push(i)
    started = time.perf_counter()
    for _ in range(100_000):
        big.get_min()
    assert time.perf_counter() - started < 0.5, "get_min must be O(1), not a scan"
