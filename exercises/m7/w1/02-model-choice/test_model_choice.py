import pytest

from model_choice import call_cost, choose_model, monthly_cost, run_cascade

SMALL = {"name": "small", "quality": 5, "input_price": 1.0, "output_price": 5.0, "latency_s": 1.0, "context": 200_000}
MEDIUM = {"name": "medium", "quality": 8, "input_price": 2.0, "output_price": 10.0, "latency_s": 3.0, "context": 1_000_000}
LARGE = {"name": "large", "quality": 10, "input_price": 5.0, "output_price": 25.0, "latency_s": 8.0, "context": 1_000_000}
MODELS = [LARGE, SMALL, MEDIUM]      # not in any special order


def test_call_cost():
    assert call_cost(MEDIUM, 10_000, 1_000) == pytest.approx(0.03)
    assert call_cost(SMALL, 0, 0) == 0


def test_picks_the_cheapest_that_is_good_enough():
    assert choose_model(MODELS, min_quality=4, max_latency_s=10, input_tokens=1000, output_tokens=500) == "small"
    assert choose_model(MODELS, min_quality=6, max_latency_s=10, input_tokens=1000, output_tokens=500) == "medium"
    assert choose_model(MODELS, min_quality=9, max_latency_s=10, input_tokens=1000, output_tokens=500) == "large"


def test_latency_limit_can_rule_out_the_best_model():
    assert choose_model(MODELS, min_quality=9, max_latency_s=5, input_tokens=100, output_tokens=100) is None
    assert choose_model(MODELS, min_quality=5, max_latency_s=2, input_tokens=100, output_tokens=100) == "small"


def test_context_size_can_rule_out_a_cheap_model():
    assert choose_model(MODELS, min_quality=1, max_latency_s=10, input_tokens=300_000, output_tokens=1_000) == "medium"
    assert choose_model(MODELS, min_quality=1, max_latency_s=10, input_tokens=199_000, output_tokens=1_000) == "small"
    assert choose_model(MODELS, min_quality=1, max_latency_s=10, input_tokens=2_000_000, output_tokens=1) is None


def test_ties_go_to_the_faster_then_the_alphabetical_name():
    a = {**SMALL, "name": "b-model"}
    b = {**SMALL, "name": "a-model"}
    c = {**SMALL, "name": "fast", "latency_s": 0.5}
    assert choose_model([a, b], min_quality=1, max_latency_s=9, input_tokens=10, output_tokens=10) == "a-model"
    assert choose_model([a, b, c], min_quality=1, max_latency_s=9, input_tokens=10, output_tokens=10) == "fast"


def test_empty_model_list():
    assert choose_model([], min_quality=1, max_latency_s=9, input_tokens=1, output_tokens=1) is None


def test_monthly_cost_without_caching():
    # per call: 10_000 * 2/1M + 1_000 * 10/1M = 0.03 → * 1000/day * 30 days = 900
    assert monthly_cost(MEDIUM, 1000, 10_000, 1_000) == pytest.approx(900.0)


def test_caching_makes_input_ten_times_cheaper():
    full = monthly_cost(MEDIUM, 1000, 10_000, 1_000, cache_hit_rate=1.0)
    # input part 0.02 → 0.002, output part 0.01 stays → 0.012 per call → 360
    assert full == pytest.approx(360.0)
    half = monthly_cost(MEDIUM, 1000, 10_000, 1_000, cache_hit_rate=0.5)
    assert half == pytest.approx((0.02 * 0.55 + 0.01) * 1000 * 30)


def test_days_parameter():
    assert monthly_cost(SMALL, 10, 1_000_000, 0, days=1) == pytest.approx(10.0)


def test_cascade_stops_at_the_first_good_answer_and_adds_up_the_cost():
    calls = []

    def ask(name):
        calls.append(name)
        return {"small": ("bad", 0.01), "medium": ("good", 0.05), "large": ("great", 0.5)}[name]

    result = run_cascade(["small", "medium", "large"], ask, lambda answer: answer in ("good", "great"))
    assert result == ("medium", "good", pytest.approx(0.06))
    assert calls == ["small", "medium"]


def test_cascade_first_try_is_good():
    result = run_cascade(["small", "large"], lambda n: ("ok", 0.01), lambda a: True)
    assert result == ("small", "ok", pytest.approx(0.01))


def test_cascade_with_no_good_answer():
    assert run_cascade(["small", "large"], lambda n: ("bad", 0.1), lambda a: False) is None
    assert run_cascade([], lambda n: ("x", 0), lambda a: True) is None
