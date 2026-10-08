import pytest

from cache_planner import block_tokens, cache_savings, first_difference, prompt_cost, simulate_cache

SYSTEM = "S" * 4000          # 1000 tokens
DOCS = "D" * 4000            # 1000 tokens


def req(t, question, bp=1, system=SYSTEM, docs=DOCS):
    return {"t": t, "blocks": [system, docs, question], "breakpoint": bp}


def test_block_tokens():
    assert block_tokens("") == 0
    assert block_tokens("abcd") == 1
    assert block_tokens("abcde") == 2


def test_first_request_writes_the_cache_second_reads_it():
    out = simulate_cache([req(0, "Q" * 40), req(10, "R" * 80)])
    assert out[0] == {"read": 0, "write": 2000, "uncached": 10}
    assert out[1] == {"read": 2000, "write": 0, "uncached": 20}


def test_a_changed_prefix_is_a_miss_and_a_new_write():
    out = simulate_cache([req(0, "q"), req(10, "q", docs="E" * 4000)])
    assert out[1]["read"] == 0 and out[1]["write"] == 2000


def test_a_silent_invalidator_in_the_first_block_kills_the_cache():
    # a timestamp at the top of the system prompt changes the whole prefix every time
    out = simulate_cache([req(i * 10, "q", system=f"2026-10-0{i} " + SYSTEM) for i in range(1, 4)])
    assert [u["read"] for u in out] == [0, 0, 0]
    assert [u["write"] for u in out] == [2003, 2003, 2003]


def test_ttl_and_refresh_on_read():
    reqs = [req(0, "q"), req(250, "q"), req(500, "q"), req(900, "q")]
    out = simulate_cache(reqs, ttl_s=300)
    assert [u["read"] for u in out] == [0, 2000, 2000, 0]      # 250 <= 300; refreshed at 250, so 500-250 <= 300; 900-500 > 300
    assert [u["write"] for u in out] == [2000, 0, 0, 2000]


def test_exactly_at_the_ttl_is_still_a_hit():
    out = simulate_cache([req(0, "q"), req(300, "q")], ttl_s=300)
    assert out[1]["read"] == 2000


def test_a_prefix_below_the_minimum_is_not_cached():
    small = [{"t": 0, "blocks": ["a" * 400, "q"], "breakpoint": 0}, {"t": 5, "blocks": ["a" * 400, "q"], "breakpoint": 0}]
    out = simulate_cache(small, min_tokens=1024)
    assert out[0] == {"read": 0, "write": 0, "uncached": 101}
    assert out[1] == {"read": 0, "write": 0, "uncached": 101}


def test_minimum_is_a_parameter():
    small = [{"t": 0, "blocks": ["a" * 400, "q"], "breakpoint": 0}, {"t": 5, "blocks": ["a" * 400, "q"], "breakpoint": 0}]
    out = simulate_cache(small, min_tokens=100)
    assert out[0]["write"] == 100 and out[1]["read"] == 100


def test_no_breakpoint_means_no_caching():
    out = simulate_cache([req(0, "q", bp=None), req(5, "q", bp=None)])
    assert out[0] == {"read": 0, "write": 0, "uncached": 2001} and out[1]["read"] == 0


def test_breakpoint_at_the_end_would_cache_the_changing_question_too():
    out = simulate_cache([req(0, "first question", bp=2), req(5, "second question", bp=2)])
    assert out[1]["read"] == 0               # the last block differs, so the whole prefix differs


def test_breakpoint_before_the_changing_part_is_the_right_place():
    out = simulate_cache([req(0, "first question", bp=1), req(5, "second question", bp=1)])
    assert out[1]["read"] == 2000


def test_different_prefixes_can_live_side_by_side():
    a = req(0, "q", docs="A" * 4000)
    b = req(1, "q", docs="B" * 4000)
    again_a = req(2, "q", docs="A" * 4000)
    out = simulate_cache([a, b, again_a])
    assert out[2]["read"] == 2000


def test_first_difference():
    assert first_difference(["a", "b", "c"], ["a", "b", "c"]) is None
    assert first_difference(["a", "b", "c"], ["a", "X", "c"]) == 1
    assert first_difference(["a", "b"], ["a", "b", "c"]) == 2
    assert first_difference(["a", "b", "c"], ["a", "b"]) == 2
    assert first_difference([], []) is None
    assert first_difference(["a"], ["b"]) == 0


def test_prompt_cost():
    # price $2 per million; 1M read (x0.1) + 1M write (x1.25) + 1M uncached (x1) = (0.1 + 1.25 + 1) * 2 = 4.7
    assert prompt_cost({"read": 1_000_000, "write": 1_000_000, "uncached": 1_000_000}, 2.0) == pytest.approx(4.7)
    assert prompt_cost({"read": 0, "write": 0, "uncached": 500_000}, 4.0) == pytest.approx(2.0)


def test_other_multipliers():
    assert prompt_cost({"read": 1_000_000, "write": 0, "uncached": 0}, 10.0, read_multiplier=0.05) == pytest.approx(0.5)
    assert prompt_cost({"read": 0, "write": 1_000_000, "uncached": 0}, 10.0, write_multiplier=2.0) == pytest.approx(20.0)


def test_caching_pays_off_with_many_requests():
    reqs = [req(i * 20, f"question {i}") for i in range(10)]
    assert cache_savings(reqs, input_price_per_m=3.0) > 0


def test_one_request_loses_the_write_premium():
    saving = cache_savings([req(0, "q")], input_price_per_m=3.0)
    assert saving == pytest.approx(-(2000 * 0.25) * 3.0 / 1_000_000)
    assert saving < 0


def test_savings_exact_value():
    # 3 requests, each 2000 + 3 tokens. cached: write 2000 + two reads 2000 each
    reqs = [req(0, "q" * 12), req(10, "q" * 12), req(20, "q" * 12)]
    plain = 3 * 2003
    weighted = (2000 * 1.25 + 3) + 2 * (2000 * 0.1 + 3)
    assert cache_savings(reqs, 1_000_000.0) == pytest.approx(plain - weighted)
