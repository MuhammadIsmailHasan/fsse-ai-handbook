"""Module 7 · W5 — A tiny eval harness (no API key needed).

An eval = a fixed set of cases + a system to test + graders that decide pass/fail.
Run it before and after every change and compare, instead of trusting a feeling.

A case:   {"id": "q1", "input": "...", "expected": "...", "tags": ["billing"]}   (expected and tags are optional)
A grader: a function  grader(case, output) -> bool
"""

import re  # noqa: F401


def contains_all(substrings: list[str]):
    """Grader: passes if EVERY substring is in the output (case-insensitive)."""
    raise NotImplementedError


def not_contains(substrings: list[str]):
    """Grader: passes if NONE of the substrings is in the output (case-insensitive)."""
    raise NotImplementedError


def matches(pattern: str):
    """Grader: passes if re.search(pattern, output) finds something (case-insensitive)."""
    raise NotImplementedError


def max_chars(limit: int):
    """Grader: passes if len(output) <= limit."""
    raise NotImplementedError


def exact_match(case: dict, output: str) -> bool:
    """Grader: output equals case["expected"] after strip() and lowercasing both."""
    raise NotImplementedError


def run_eval(system, cases: list[dict], graders: dict) -> dict:
    """Run every case through the system and every grader.

    system(case["input"]) -> output string.  If the system raises, the output is "" and the error is recorded as
    "<ExceptionClass>: <message>" (the run continues).
    graders: {"name": grader_function}. Every grader runs on every case, even after an error (on the "" output).

    Return:
      {
        "total": n,
        "passed": number of cases that are ok,
        "pass_rate": passed / total   (0.0 if there are no cases),
        "by_grader": {name: share of cases where that grader passed},
        "by_tag": {tag: pass_rate of the cases with that tag},
        "failures": [ids of cases that are not ok, in case order],
        "results": [{"id", "output", "passed": {grader name: bool}, "error": str | None, "ok": bool}, ...],
      }
    A case is ok when there was no error AND every grader passed.
    """
    raise NotImplementedError


def compare_runs(old: dict, new: dict) -> dict:
    """Compare two run_eval results case by case (match by id; only ids present in BOTH runs count).
    Return {"fixed": [ids not ok before and ok now], "broken": [ids ok before and not ok now],
            "same_pass": number ok in both, "same_fail": number not ok in both}   ("fixed"/"broken" in the order of `new` results)."""
    raise NotImplementedError


def gate(old: dict, new: dict, min_pass_rate: float, max_broken: int = 0) -> tuple[bool, list[str]]:
    """Should this change be released? Return (ok, reasons).
      - if new["pass_rate"] < min_pass_rate:   reason "pass rate 0.80 is below 0.90"  (two decimals, exactly this wording)
      - if more than max_broken cases broke:   reason "3 cases broke: a, b, c"          (count, then ids joined by ", ")
    ok is True only when there are no reasons."""
    raise NotImplementedError
