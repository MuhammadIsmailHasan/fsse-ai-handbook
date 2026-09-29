"""Module 3 · W2 — Sequential vs concurrent I/O (solution)."""

import asyncio


class Tracker:
    def __init__(self):
        self.in_flight = 0
        self.max_in_flight = 0


async def fetch(tracker: Tracker, item_id: int) -> int:
    tracker.in_flight += 1
    tracker.max_in_flight = max(tracker.max_in_flight, tracker.in_flight)
    await asyncio.sleep(0)
    tracker.in_flight -= 1
    return item_id


async def fetch_all_sequential(tracker: Tracker, ids: list[int]) -> list[int]:
    results = []
    for item_id in ids:
        results.append(await fetch(tracker, item_id))
    return results


async def fetch_all_concurrent(tracker: Tracker, ids: list[int]) -> list[int]:
    return list(await asyncio.gather(*(fetch(tracker, item_id) for item_id in ids)))
