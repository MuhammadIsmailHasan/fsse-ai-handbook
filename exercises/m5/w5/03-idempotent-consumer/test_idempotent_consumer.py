"""Checks for idempotent_consumer.py. Don't edit this file."""

from idempotent_consumer import apply_once


def test_no_duplicates_sums_everything():
    assert apply_once([("m1", 100), ("m2", 50), ("m3", 25)]) == (175, ["m1", "m2", "m3"])


def test_duplicate_is_applied_once():
    assert apply_once([("m1", 100), ("m2", 50), ("m1", 100)]) == (150, ["m1", "m2"])


def test_applied_ids_keep_first_seen_order():
    events = [("b", 1), ("a", 2), ("b", 1), ("c", 3), ("a", 2)]
    assert apply_once(events) == (6, ["b", "a", "c"])


def test_empty_stream():
    assert apply_once([]) == (0, [])


def test_repeated_duplicate_still_applied_once():
    assert apply_once([("m1", 10), ("m1", 10), ("m1", 10)]) == (10, ["m1"])
