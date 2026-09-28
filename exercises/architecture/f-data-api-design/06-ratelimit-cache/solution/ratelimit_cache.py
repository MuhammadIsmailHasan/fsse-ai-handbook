"""Architecture · F — Token-bucket limiter and cache-aside (solution)."""


class TokenBucket:
    def __init__(self, capacity: float, refill_per_sec: float):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.tokens = float(capacity)
        self.last = 0.0

    def allow(self, now: float, cost: float = 1) -> bool:
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.refill_per_sec)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


class CacheAside:
    def __init__(self):
        self.store: dict = {}

    def get(self, key, now: float, ttl: float, loader):
        entry = self.store.get(key)
        if entry is not None and entry["expires"] > now:
            return entry["value"], "hit"
        value = loader()
        self.store[key] = {"value": value, "expires": now + ttl}
        return value, "miss"

    def invalidate(self, key) -> None:
        self.store.pop(key, None)
