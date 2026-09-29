"""Module 3 · W2 — Sequential vs concurrent I/O.

A fake async `fetch` simulates an I/O call. A shared Tracker counts how many
calls are "in flight" at once, so we can PROVE (no timing) that:
- fetch_all_sequential never has more than 1 call in flight,
- fetch_all_concurrent (asyncio.gather) has all of them in flight at once.
"""

import asyncio


class Tracker:
    def __init__(self):
        self.in_flight = 0
        self.max_in_flight = 0


async def fetch(tracker: Tracker, item_id: int) -> int:
    """Fake I/O call: enter, yield to the loop, leave. Returns the id."""
    tracker.in_flight += 1
    tracker.max_in_flight = max(tracker.max_in_flight, tracker.in_flight)
    await asyncio.sleep(0)  # yield control to the event loop
    tracker.in_flight -= 1
    return item_id


async def fetch_all_sequential(tracker: Tracker, ids: list[int]) -> list[int]:
    """Await each fetch one after another. Return results in order."""
    # YOUR CODE HERE
    return []


async def fetch_all_concurrent(tracker: Tracker, ids: list[int]) -> list[int]:
    """Run all fetches at once with asyncio.gather. Return results in input order."""
    # YOUR CODE HERE
    return []
