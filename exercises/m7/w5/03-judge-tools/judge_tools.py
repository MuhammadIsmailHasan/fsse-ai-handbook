"""Module 7 · W5 — LLM-as-judge, and checking the judge (no API key needed).

Many answers cannot be graded by string matching ("is this a helpful, correct reply?"). A model can act as the
judge. But a judge is a model too: it can be biased, inconsistent, or simply wrong, so you MEASURE it against humans.
"""

import json  # noqa: F401
from collections.abc import Callable


class JudgeError(ValueError):
    """The judge's reply could not be understood."""


def judge_prompt(question: str, answer: str, reference: str, rubric: str) -> str:
    """Build the judge prompt EXACTLY like this (lines joined with "\\n"):

        You are grading an answer to a customer question.
        Rubric: <rubric>

        <question>
        <question text>
        </question>

        <reference>
        <reference text>
        </reference>

        <answer>
        <answer text>
        </answer>

        Reply with JSON only: {"score": <integer 1-5>, "reasoning": "<one short sentence>"}
    """
    raise NotImplementedError


def parse_judge(reply: str) -> dict:
    """Read the judge's reply and return {"score": int, "reasoning": str}.

    The JSON may be plain, inside a ``` fence, or surrounded by words. Take the first complete {...} object that
    parses as JSON. The score must be an integer from 1 to 5 (a bool, a float like 4.5, or a string is NOT valid;
    a float with a whole value such as 4.0 is not valid either); "reasoning" must be a string (a missing reasoning
    becomes ""). Otherwise raise JudgeError.
    """
    raise NotImplementedError


def accuracy(a: list, b: list) -> float:
    """Share of positions where the two label lists agree. Different lengths: ValueError. Empty lists: 1.0."""
    raise NotImplementedError


def cohens_kappa(a: list, b: list) -> float:
    """Agreement beyond chance: (po - pe) / (1 - pe).
    po = observed agreement (accuracy). pe = sum over labels of (share of label in a) * (share of label in b).
    If pe == 1: return 1.0 when po == 1, otherwise 0.0. Different lengths: ValueError. Empty lists: 1.0."""
    raise NotImplementedError


def confusion_matrix(human: list, judge: list, labels: list) -> dict:
    """{human_label: {judge_label: count}} with EVERY label from `labels` as a key at both levels (zeros included)."""
    raise NotImplementedError


def swap_consistency(pairs: list[tuple[str, str, str]], judge_fn: Callable[[str, str, str], str]) -> float:
    """Position bias test for a pairwise judge. pairs: [(question, answer_a, answer_b), ...]
    judge_fn(question, first, second) -> "first" | "second" | "tie".
    Ask each pair in both orders: (a, b) and (b, a). The judge is CONSISTENT on a pair if it prefers the same ANSWER
    in both orders, or says "tie" in both. Return the share of consistent pairs (1.0 for no pairs)."""
    raise NotImplementedError


def best_threshold(scores: list[int], human_pass: list[bool], candidates=(1, 2, 3, 4, 5)) -> int:
    """Which score threshold t (judge says PASS when score >= t) best matches the humans?
    Pick the t with the highest accuracy; if several tie, pick the LARGER t. Different lengths: ValueError."""
    raise NotImplementedError
