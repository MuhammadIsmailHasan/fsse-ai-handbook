from replicas import apply, merge_counter, merge_lww


def test_apply_keeps_newest():
    state: dict = {}
    apply(state, "name", "Ismail", ts=1)
    apply(state, "name", "OLD", ts=0)  # older → ignored
    assert state["name"] == ("Ismail", 1)
    apply(state, "name", "Muhammad", ts=2)  # newer → wins
    assert state["name"] == ("Muhammad", 2)


def test_lww_converges_both_replicas():
    # During a partition, each replica took different writes.
    a = {"title": ("A-title", 2), "color": ("red", 1)}
    b = {"title": ("B-title", 1), "size": ("L", 3)}
    merged_ab = merge_lww(a, b)
    merged_ba = merge_lww(b, a)
    # Order of merge doesn't matter — both converge to the same state.
    assert merged_ab == merged_ba
    assert merged_ab == {
        "title": ("A-title", 2),  # ts 2 beats ts 1
        "color": ("red", 1),
        "size": ("L", 3),
    }


def test_lww_can_drop_a_concurrent_edit():
    # Two edits to the SAME key with the SAME timestamp: one is lost (tie-break).
    a = {"bio": ("hello from A", 5)}
    b = {"bio": ("hello from B", 5)}
    merged = merge_lww(a, b)
    assert merged["bio"] in {("hello from A", 5), ("hello from B", 5)}
    # Only one survives — the other edit is gone. This is LWW's weakness.
    assert len(merged) == 1


def test_counter_merge_loses_no_increments():
    # Both data centers counted likes during the partition.
    a = {"post_1": 3, "post_2": 1}
    b = {"post_1": 4}
    merged = merge_counter(a, b)
    # post_1 = 3 + 4 = 7 (nothing dropped); post_2 stays 1.
    assert merged == {"post_1": 7, "post_2": 1}
    # Commutative: same result whichever side you merge first.
    assert merge_counter(b, a) == merged
