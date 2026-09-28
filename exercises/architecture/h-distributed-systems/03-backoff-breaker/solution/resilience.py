"""Architecture · H — Exponential backoff and a circuit breaker (solution)."""


def backoff_delay(attempt: int, base: float = 0.5, cap: float = 30.0) -> float:
    return min(cap, base * (2 ** attempt))


class CircuitBreaker:
    def __init__(self, failure_threshold: int, cooldown: float):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.state = "closed"
        self.failures = 0
        self.opened_at = None

    def allow(self, now: float) -> bool:
        if self.state == "open":
            if self.opened_at is not None and now - self.opened_at >= self.cooldown:
                self.state = "half-open"
                return True
            return False
        return True  # closed or half-open

    def on_success(self) -> None:
        self.state = "closed"
        self.failures = 0
        self.opened_at = None

    def on_failure(self, now: float) -> None:
        if self.state == "half-open":
            self.state = "open"
            self.opened_at = now
            return
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = now
