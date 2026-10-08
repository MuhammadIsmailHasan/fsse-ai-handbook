import pytest

from eval_harness import compare_runs, contains_all, exact_match, gate, matches, max_chars, not_contains, run_eval

CASES = [
    {"id": "a", "input": "refund?", "expected": "7 days", "tags": ["billing"]},
    {"id": "b", "input": "shipping?", "expected": "free", "tags": ["shipping", "billing"]},
    {"id": "c", "input": "password?", "expected": "reset link"},
]
ANSWERS = {"refund?": "Refunds take 7 days.", "shipping?": "Shipping costs Rp 20.000.", "password?": "Use the reset link."}


def system(text):
    return ANSWERS[text]


def has_expected(case, output):
    return case["expected"].lower() in output.lower()


GRADERS = {"expected": has_expected, "short": max_chars(20)}


def test_basic_graders():
    case = {}
    assert contains_all(["a", "B"])(case, "a b c") is True
    assert contains_all(["a", "z"])(case, "a b c") is False
    assert not_contains(["x", "y"])(case, "abc") is True
    assert not_contains(["x", "b"])(case, "abc") is False
    assert matches(r"\d+ days")(case, "In 7 DAYS") is True
    assert matches(r"\d+ days")(case, "soon") is False
    assert max_chars(5)(case, "12345") is True and max_chars(5)(case, "123456") is False


def test_exact_match():
    assert exact_match({"expected": " Yes "}, "yes\n") is True
    assert exact_match({"expected": "yes"}, "yes!") is False


def test_run_eval_summary():
    run = run_eval(system, CASES, GRADERS)
    assert run["total"] == 3 and run["passed"] == 2
    assert run["pass_rate"] == pytest.approx(2 / 3)
    assert run["failures"] == ["b"]
    assert run["by_grader"] == {"expected": pytest.approx(2 / 3), "short": pytest.approx(2 / 3)}
    assert run["by_tag"] == {"billing": pytest.approx(0.5), "shipping": pytest.approx(0.0)}


def test_run_eval_results_per_case():
    run = run_eval(system, CASES, GRADERS)
    assert [r["id"] for r in run["results"]] == ["a", "b", "c"]
    b = run["results"][1]
    assert b == {"id": "b", "output": "Shipping costs Rp 20.000.", "passed": {"expected": False, "short": False},
                 "error": None, "ok": False}


def test_a_crashing_system_is_recorded_and_the_run_continues():
    def flaky(text):
        if text == "shipping?":
            raise TimeoutError("model timed out")
        return ANSWERS[text]

    run = run_eval(flaky, CASES, GRADERS)
    bad = run["results"][1]
    assert bad["error"] == "TimeoutError: model timed out" and bad["output"] == "" and bad["ok"] is False
    assert run["results"][2]["ok"] is True
    assert run["failures"] == ["b"]


def test_an_error_fails_the_case_even_if_every_grader_passes():
    def crashes(text):
        raise ValueError("boom")

    run = run_eval(crashes, [{"id": "x", "input": "q"}], {"anything": lambda case, output: True})
    assert run["results"][0]["passed"] == {"anything": True} and run["results"][0]["ok"] is False


def test_no_cases():
    run = run_eval(system, [], GRADERS)
    assert run["total"] == 0 and run["pass_rate"] == 0.0 and run["failures"] == []
    assert run["by_grader"] == {"expected": 0.0, "short": 0.0}


def test_compare_runs():
    old = run_eval(system, CASES, GRADERS)                       # a ok, b fail, c ok
    improved = dict(ANSWERS, **{"shipping?": "Shipping is free."})
    regressed = dict(improved, **{"refund?": "No idea."})
    new = run_eval(lambda t: regressed[t], CASES, GRADERS)       # a fail, b ok, c ok
    assert compare_runs(old, new) == {"fixed": ["b"], "broken": ["a"], "same_pass": 1, "same_fail": 0}


def test_compare_runs_ignores_ids_that_are_not_in_both():
    old = run_eval(system, CASES[:2], GRADERS)
    new = run_eval(system, CASES[1:], GRADERS)
    assert compare_runs(old, new) == {"fixed": [], "broken": [], "same_pass": 0, "same_fail": 1}


def test_gate_passes_when_nothing_broke_and_the_rate_is_high_enough():
    old = run_eval(system, CASES, GRADERS)
    new = run_eval(lambda t: dict(ANSWERS, **{"shipping?": "Free shipping."})[t], CASES, GRADERS)
    assert gate(old, new, 0.9) == (True, [])


def test_gate_blocks_a_low_pass_rate():
    old = run_eval(system, CASES, GRADERS)
    ok, reasons = gate(old, old, 0.9)
    assert ok is False and reasons == ["pass rate 0.67 is below 0.90"]


def test_gate_blocks_regressions_even_when_the_rate_is_fine():
    old = run_eval(system, CASES, GRADERS)
    fixed_one_broke_one = dict(ANSWERS, **{"shipping?": "Free shipping.", "refund?": "No idea."})
    new = run_eval(lambda t: fixed_one_broke_one[t], CASES, GRADERS)
    ok, reasons = gate(old, new, 0.5)
    assert ok is False and reasons == ["1 cases broke: a"]
    assert gate(old, new, 0.5, max_broken=1) == (True, [])


def test_gate_can_report_both_reasons():
    old = run_eval(system, CASES, GRADERS)
    worse = run_eval(lambda t: "No idea.", CASES, GRADERS)
    ok, reasons = gate(old, worse, 0.9)
    assert ok is False and len(reasons) == 2 and reasons[0].startswith("pass rate")
    assert reasons[1] == "2 cases broke: a, c"
