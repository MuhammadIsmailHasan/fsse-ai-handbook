"""Architecture · B — A small TTL cache with an injected clock."""

import time
from collections.abc import Callable
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: float, clock: Callable[[], float] = time.monotonic):
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self.hits = 0
        self.misses = 0
        # YOUR CODE HERE: where will entries live?

    def set(self, key: str, value: Any) -> None:
        # YOUR CODE HERE
        pass

    def get(self, key: str, default: Any = None) -> Any:
        # YOUR CODE HERE
        return default

    def delete(self, key: str) -> None:
        # YOUR CODE HERE
        pass


def cached_fetch(cache: TTLCache, key: str, fetch: Callable[[], Any]) -> Any:
    # YOUR CODE HERE
    return fetch()
