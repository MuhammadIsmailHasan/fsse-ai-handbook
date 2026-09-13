"""Reference solution."""

import time
from collections.abc import Callable
from typing import Any

_MISSING = object()  # a unique marker, so cached falsy values (0, "", None) still count as hits


class TTLCache:
    def __init__(self, ttl_seconds: float, clock: Callable[[], float] = time.monotonic):
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self.hits = 0
        self.misses = 0
        self._entries: dict[str, tuple[Any, float]] = {}

    def set(self, key: str, value: Any) -> None:
        self._entries[key] = (value, self._clock() + self.ttl_seconds)

    def get(self, key: str, default: Any = None) -> Any:
        value, expires_at = self._entries.get(key, (_MISSING, 0.0))
        if value is _MISSING or self._clock() >= expires_at:
            self._entries.pop(key, None)
            self.misses += 1
            return default
        self.hits += 1
        return value

    def delete(self, key: str) -> None:
        self._entries.pop(key, None)


def cached_fetch(cache: TTLCache, key: str, fetch: Callable[[], Any]) -> Any:
    value = cache.get(key, default=_MISSING)
    if value is not _MISSING:
        return value
    value = fetch()
    if value is not None:
        cache.set(key, value)
    return value
