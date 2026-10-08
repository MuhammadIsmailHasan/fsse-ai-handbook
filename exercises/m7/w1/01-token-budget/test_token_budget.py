import math

import pytest

from token_budget import apply_temperature, estimate_tokens, fit_history, request_cost


def test_estimate_tokens_rounds_up():
    assert estimate_tokens("") == 0
    assert estimate_tokens("a") == 1
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("abcde") == 2
    assert estimate_tokens("x" * 400) == 100


def test_request_cost():
    assert request_cost(1000, 500, 3.0, 15.0) == pytest.approx(0.0105)
    assert request_cost(0, 0, 3.0, 15.0) == 0
    assert request_cost(1_000_000, 0, 2.0, 10.0) == pytest.approx(2.0)
    assert request_cost(0, 1_000_000, 2.0, 10.0) == pytest.approx(10.0)


def msg(role, n_chars):
    return {"role": role, "content": "x" * n_chars}     # 40 chars = 10 tokens + 4 overhead = 14


def test_everything_fits_so_nothing_is_dropped():
    messages = [msg("system", 40), msg("user", 40), msg("assistant", 40), msg("user", 40)]
    assert fit_history(messages, max_context=1000, reserve_for_output=100) == messages


def test_oldest_messages_go_first_and_the_chat_starts_with_user():
    s, u1, a1, u2 = msg("system", 40), msg("user", 40), msg("assistant", 40), msg("user", 40)
    # total = 56, budget = 60 - 10 = 50 → drop u1; a1 would now come first → drop it too
    assert fit_history([s, u1, a1, u2], max_context=60, reserve_for_output=10) == [s, u2]


def test_keeps_a_whole_turn_when_the_budget_allows():
    s = msg("system", 40)
    u1, a1, u2, a2, u3 = msg("user", 40), msg("assistant", 40), msg("user", 40), msg("assistant", 40), msg("user", 40)
    # total 6*14 = 84; budget 56 → must keep 4 messages: s + (u2 a2 u3 = 42)
    assert fit_history([s, u1, a1, u2, a2, u3], max_context=66, reserve_for_output=10) == [s, u2, a2, u3]


def test_works_without_a_system_message():
    u1, a1, u2 = msg("user", 40), msg("assistant", 40), msg("user", 40)
    assert fit_history([u1, a1, u2], max_context=30, reserve_for_output=0) == [u2]


def test_last_message_is_always_kept_or_it_is_an_error():
    s, big = msg("system", 40), msg("user", 4000)
    with pytest.raises(ValueError):
        fit_history([s, big], max_context=100, reserve_for_output=10)


def test_system_plus_last_over_budget_is_an_error():
    with pytest.raises(ValueError):
        fit_history([msg("system", 400), msg("user", 40)], max_context=60, reserve_for_output=10)


def test_input_is_not_changed_and_empty_is_fine():
    messages = [msg("system", 40), msg("user", 40), msg("assistant", 40), msg("user", 40)]
    snapshot = [dict(m) for m in messages]
    fit_history(messages, max_context=60, reserve_for_output=10)
    assert messages == snapshot
    assert fit_history([], max_context=100, reserve_for_output=10) == []


def test_probabilities_add_up_to_one_and_keep_the_order():
    probs = apply_temperature({"a": 2.0, "b": 1.0, "c": 0.0}, 1.0)
    assert sum(probs.values()) == pytest.approx(1.0)
    assert probs["a"] == pytest.approx(math.e**2 / (math.e**2 + math.e + 1))
    assert probs["a"] > probs["b"] > probs["c"]


def test_lower_temperature_is_sharper_higher_is_flatter():
    logits = {"a": 2.0, "b": 1.0, "c": 0.0}
    cold, normal, hot = (apply_temperature(logits, t) for t in (0.3, 1.0, 3.0))
    assert cold["a"] > normal["a"] > hot["a"]
    assert cold["c"] < normal["c"] < hot["c"]


def test_very_high_temperature_is_almost_uniform():
    probs = apply_temperature({"a": 2.0, "b": 1.0, "c": 0.0}, 100.0)
    assert all(abs(p - 1 / 3) < 0.02 for p in probs.values())


def test_temperature_zero_always_picks_the_best():
    assert apply_temperature({"a": 2.0, "b": 5.0, "c": 0.0}, 0) == {"a": 0.0, "b": 1.0, "c": 0.0}
    assert apply_temperature({"a": 1.0, "b": 1.0}, 0) == {"a": 1.0, "b": 0.0}


def test_negative_temperature_is_an_error():
    with pytest.raises(ValueError):
        apply_temperature({"a": 1.0}, -0.5)


def test_large_logits_do_not_overflow():
    probs = apply_temperature({"a": 1000.0, "b": 999.0}, 1.0)
    assert probs["a"] == pytest.approx(math.e / (math.e + 1))
    assert sum(probs.values()) == pytest.approx(1.0)
