import asyncio

from async_io import Tracker, fetch_all_concurrent, fetch_all_sequential


def test_sequential_returns_in_order_and_one_at_a_time():
    tracker = Tracker()
    ids = [1, 2, 3, 4]
    results = asyncio.run(fetch_all_sequential(tracker, ids))
    assert results == ids
    assert tracker.max_in_flight == 1  # never more than one call at a time


def test_concurrent_runs_all_at_once():
    tracker = Tracker()
    ids = [1, 2, 3, 4]
    results = asyncio.run(fetch_all_concurrent(tracker, ids))
    assert results == ids  # gather preserves input order
    assert tracker.max_in_flight == len(ids)  # all in flight simultaneously


def test_both_handle_empty():
    assert asyncio.run(fetch_all_sequential(Tracker(), [])) == []
    assert asyncio.run(fetch_all_concurrent(Tracker(), [])) == []
