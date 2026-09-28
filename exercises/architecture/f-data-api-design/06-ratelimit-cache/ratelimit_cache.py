"""Architecture · F — Token-bucket limiter and cache-aside.

Both take an explicit `now` (float seconds) so the tests are deterministic —
never read the real clock here.
"""


class TokenBucket:
    """Allows short bursts up to `capacity`, refilling `refill_per_sec` tokens/second.

    Each allowed request spends `cost` tokens; when the bucket can't cover the
    cost, the request is rejected (your API would answer HTTP 429).
    """

    def __init__(self, capacity: float, refill_per_sec: float):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.tokens = float(capacity)
        self.last = 0.0

    def allow(self, now: float, cost: float = 1) -> bool:
        # YOUR CODE HERE
        return False


class CacheAside:
    """A tiny cache-aside store. On a miss it calls `loader()` and remembers the
    result with a TTL; hits within the TTL skip the loader."""

    def __init__(self):
        self.store: dict = {}

    def get(self, key, now: float, ttl: float, loader):
        """Return (value, "hit"|"miss"). A miss = absent OR expired (expires <= now)."""
        # YOUR CODE HERE
        return None, "miss"

    def invalidate(self, key) -> None:
        """Drop a key so the next get is a miss (call this on write)."""
        # YOUR CODE HERE
        return None
