import pytest

from shard_router import keys_moved_on_resize, route, shard_for


def test_shard_for_in_range_and_stable():
    for key in ["user_1", "user_2", 42, "ismail@example.com"]:
        s = shard_for(key, 4)
        assert 0 <= s < 4
        # Deterministic: same key + same shard count => same shard, every call.
        assert shard_for(key, 4) == s


def test_shard_spreads_keys():
    # 400 keys over 4 shards should touch every shard (roughly even, never all in one).
    keys = [f"user_{i}" for i in range(400)]
    counts = [0, 0, 0, 0]
    for key in keys:
        counts[shard_for(key, 4)] += 1
    assert all(c > 0 for c in counts)


def test_route_reads_and_writes():
    assert route("insert") == "primary"
    assert route("update") == "primary"
    assert route("delete") == "primary"
    assert route("read") == "replica"
    assert route("select") == "replica"
    assert route("GET") == "replica"  # case-insensitive
    with pytest.raises(ValueError):
        route("frobnicate")


def test_naive_resize_moves_most_keys():
    keys = [f"user_{i}" for i in range(1000)]
    moved = keys_moved_on_resize(keys, 4, 5)
    # Naive modulo sharding reshuffles the majority of keys on a resize.
    assert moved > len(keys) // 2
    # Going to the same shard count moves nothing.
    assert keys_moved_on_resize(keys, 4, 4) == 0
