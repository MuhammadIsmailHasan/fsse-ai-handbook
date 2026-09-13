import random

import pytest

from rpn import evaluate_rpn


@pytest.mark.parametrize(
    ("tokens", "expected"),
    [
        (["2", "1", "+", "3", "*"], 9),
        (["4", "13", "5", "/", "+"], 6),
        (["-7", "2", "/"], -3),
        (["7", "-2", "/"], -3),
        (["-8", "-2", "/"], 4),
        (["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"], 22),
        (["42"], 42),
        (["5", "8", "-"], -3),
    ],
)
def test_examples(tokens, expected):
    assert evaluate_rpn(tokens) == expected


@pytest.mark.parametrize("tokens", [[], ["+"], ["1", "+"], ["1", "2"], ["1", "2", "^"], ["one"]])
def test_invalid_expressions(tokens):
    with pytest.raises(ValueError):
        evaluate_rpn(tokens)


def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        evaluate_rpn(["1", "0", "/"])


def to_rpn_and_value(rng, depth):
    if depth == 0 or rng.random() < 0.3:
        n = rng.randint(-9, 9)
        return [str(n)], n
    left_tokens, left = to_rpn_and_value(rng, depth - 1)
    right_tokens, right = to_rpn_and_value(rng, depth - 1)
    op = rng.choice("+-*/")
    if op == "/" and right == 0:
        op = "+"
    value = {"+": left + right, "-": left - right, "*": left * right, "/": int(left / right) if op == "/" else 0}[op]
    return left_tokens + right_tokens + [op], value


def test_random_expressions():
    rng = random.Random(6)
    for _ in range(500):
        tokens, value = to_rpn_and_value(rng, 4)
        assert evaluate_rpn(tokens) == value
