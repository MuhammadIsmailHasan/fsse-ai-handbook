from collections import deque


class RateLimiter:
    """Sliding log: amortized O(1) per call (each timestamp is appended and evicted once), O(limit) memory per user."""

    def __init__(self, limit: int, window: float):
        self.limit = limit
        self.window = window
        self._log: dict[str, deque[float]] = {}

    def allow(self, user_id: str, now: float) -> bool:
        log = self._log.setdefault(user_id, deque())
        while log and now - log[0] >= self.window:
            log.popleft()
        if len(log) >= self.limit:
            return False
        log.append(now)
        return True
