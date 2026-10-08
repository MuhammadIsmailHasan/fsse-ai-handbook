import pytest

from judge_tools import (
    JudgeError, accuracy, best_threshold, cohens_kappa, confusion_matrix, judge_prompt, parse_judge, swap_consistency,
)


def test_judge_prompt_layout():
    assert judge_prompt("How long is a refund?", "7 days.", "Refunds take 7 days.", "Correct and polite") == (
        "You are grading an answer to a customer question.\n"
        "Rubric: Correct and polite\n"
        "\n"
        "<question>\nHow long is a refund?\n</question>\n"
        "\n"
        "<reference>\nRefunds take 7 days.\n</reference>\n"
        "\n"
        "<answer>\n7 days.\n</answer>\n"
        "\n"
        'Reply with JSON only: {"score": <integer 1-5>, "reasoning": "<one short sentence>"}'
    )


def test_parse_plain_fenced_and_surrounded():
    assert parse_judge('{"score": 4, "reasoning": "Correct but terse."}') == {"score": 4, "reasoning": "Correct but terse."}
    assert parse_judge('```json\n{"score": 2, "reasoning": "Wrong number."}\n```') == {"score": 2, "reasoning": "Wrong number."}
    assert parse_judge('Sure! {"score": 5, "reasoning": "Perfect {really}."} Hope that helps.') == {"score": 5, "reasoning": "Perfect {really}."}


def test_missing_reasoning_becomes_empty():
    assert parse_judge('{"score": 3}') == {"score": 3, "reasoning": ""}


@pytest.mark.parametrize(
    "reply",
    ['{"score": 0}', '{"score": 6}', '{"score": 4.5}', '{"score": 4.0}', '{"score": "4"}', '{"score": true}',
     '{"reasoning": "no score"}', 'no json here', '', '{"score": 4, "reasoning": 5}', '[1, 2]'],
)
def test_bad_replies(reply):
    with pytest.raises(JudgeError):
        parse_judge(reply)


def test_a_broken_first_object_is_skipped():
    assert parse_judge('{oops} then {"score": 1, "reasoning": "bad"}')["score"] == 1


def test_accuracy_and_lengths():
    assert accuracy([1, 1, 0, 0], [1, 0, 0, 0]) == 0.75
    assert accuracy([], []) == 1.0
    with pytest.raises(ValueError):
        accuracy([1], [1, 2])


def test_kappa():
    human = [1, 1, 1, 0, 0, 0, 1, 0]
    assert cohens_kappa(human, human) == pytest.approx(1.0)
    # po = 0.75; both lists: 4 ones? human has 4 ones/4 zeros; judge has 4 ones/4 zeros → pe = 0.5 → kappa = 0.5
    judge = [1, 1, 0, 0, 0, 1, 1, 0]
    assert accuracy(human, judge) == 0.75
    assert cohens_kappa(human, judge) == pytest.approx(0.5)


def test_kappa_is_low_when_the_judge_just_says_pass_to_everything():
    human = [1, 0, 1, 0, 0, 0, 0, 0, 0, 1]          # mostly fail
    judge = [1] * 10
    assert accuracy(human, judge) == 0.3
    assert cohens_kappa(human, judge) == pytest.approx(0.0)


def test_kappa_edge_cases():
    assert cohens_kappa([], []) == 1.0
    assert cohens_kappa(["a", "a"], ["a", "a"]) == 1.0            # pe == 1 and po == 1
    assert cohens_kappa(["a", "a"], ["b", "b"]) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        cohens_kappa([1], [])


def test_confusion_matrix():
    m = confusion_matrix(["pass", "pass", "fail", "fail", "fail"], ["pass", "fail", "fail", "fail", "pass"], ["pass", "fail"])
    assert m == {"pass": {"pass": 1, "fail": 1}, "fail": {"pass": 1, "fail": 2}}
    assert confusion_matrix([], [], ["a", "b"]) == {"a": {"a": 0, "b": 0}, "b": {"a": 0, "b": 0}}


def test_swap_consistency_for_a_fair_judge():
    def fair(question, first, second):
        return "first" if len(first) > len(second) else "second" if len(second) > len(first) else "tie"

    pairs = [("q", "long answer here", "short"), ("q", "x", "xx"), ("q", "same", "same")]
    assert swap_consistency(pairs, fair) == 1.0


def test_swap_consistency_for_a_judge_that_always_prefers_the_first_position():
    biased = lambda question, first, second: "first"
    pairs = [("q", "a", "bb"), ("q", "ccc", "d")]
    assert swap_consistency(pairs, biased) == 0.0


def test_swap_consistency_mixed_and_empty():
    def partly(question, first, second):
        return "first" if "x" in first + second else ("first" if first < second else "second")

    pairs = [("q", "x1", "y"), ("q", "a", "b")]          # first pair: biased toward position; second: consistent
    assert swap_consistency(pairs, partly) == 0.5
    assert swap_consistency([], partly) == 1.0


def test_swap_consistency_tie_in_both_orders_is_consistent_but_tie_in_one_is_not():
    always_tie = lambda q, a, b: "tie"
    assert swap_consistency([("q", "a", "b")], always_tie) == 1.0
    calls = []

    def tie_once(q, a, b):
        calls.append((a, b))
        return "tie" if len(calls) % 2 == 1 else "first"

    assert swap_consistency([("q", "a", "b")], tie_once) == 0.0


def test_best_threshold():
    scores = [5, 4, 4, 3, 2, 2, 1, 1]
    human = [True, True, True, False, False, False, False, False]
    assert best_threshold(scores, human) == 4
    assert best_threshold([5, 5, 5], [True, True, True]) == 5          # ties → the larger threshold
    assert best_threshold([1, 1], [False, False]) == 5
    with pytest.raises(ValueError):
        best_threshold([1], [])
