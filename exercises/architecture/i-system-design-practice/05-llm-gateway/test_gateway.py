import pytest

from gateway import LLMGateway, estimate_cost


def test_estimate_cost():
    assert estimate_cost(1000, 0.5) == pytest.approx(0.5)
    assert estimate_cost(2500, 2.0) == pytest.approx(5.0)
    assert estimate_cost(0, 2.0) == 0.0


def make_provider(name, text="answer", tokens=1000, fails=False):
    calls = {"n": 0}

    def fn(prompt):
        calls["n"] += 1
        if fails:
            raise RuntimeError(f"{name} down")
        return {"text": f"{text} from {name}", "tokens": tokens}

    return (name, fn), calls


def test_success_cache_and_cost():
    provider, calls = make_provider("A", tokens=1000)
    gw = LLMGateway(providers=[provider], price_per_1k=2.0)

    first = gw.complete("hello")
    assert first["provider"] == "A"
    assert first["cached"] is False
    assert first["cost"] == pytest.approx(2.0)   # 1000 tokens * $2/1k
    assert gw.total_cost == pytest.approx(2.0)
    assert calls["n"] == 1

    # Same prompt → cache hit, no provider call, no extra cost.
    again = gw.complete("hello")
    assert again["cached"] is True
    assert again["cost"] == 0.0
    assert again["text"] == first["text"]
    assert gw.total_cost == pytest.approx(2.0)    # unchanged
    assert calls["n"] == 1                         # provider not called again


def test_fallback_to_next_provider():
    bad, bad_calls = make_provider("A", fails=True)
    good, good_calls = make_provider("B", tokens=500)
    gw = LLMGateway(providers=[bad, good], price_per_1k=4.0)

    result = gw.complete("hi")
    assert result["provider"] == "B"              # fell back past the failing A
    assert result["cost"] == pytest.approx(2.0)   # 500 * $4/1k
    assert bad_calls["n"] == 1 and good_calls["n"] == 1


def test_all_providers_fail_raises():
    a, _ = make_provider("A", fails=True)
    b, _ = make_provider("B", fails=True)
    gw = LLMGateway(providers=[a, b], price_per_1k=1.0)
    with pytest.raises(RuntimeError):
        gw.complete("hi")
    assert gw.total_cost == 0.0
