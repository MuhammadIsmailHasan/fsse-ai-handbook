"""Architecture · H — Exponential backoff and a circuit breaker.

- backoff_delay: wait longer after each attempt, capped.
- CircuitBreaker: closed → open → half-open, so you stop calling a dead service.

The breaker takes an explicit `now` (float seconds) so tests are deterministic.
"""


def backoff_delay(attempt: int, base: float = 0.5, cap: float = 30.0) -> float:
    """Delay before a retry: base * 2**attempt, capped at `cap`. attempt starts at 0."""
    # YOUR CODE HERE
    return -1.0


class CircuitBreaker:
    """Three states:
    - CLOSED: calls allowed; count consecutive failures.
    - OPEN: calls blocked until `cooldown` has passed, then move to HALF-OPEN.
    - HALF-OPEN: allow one trial; success → CLOSED, failure → OPEN again.
    """

    def __init__(self, failure_threshold: int, cooldown: float):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.state = "closed"
        self.failures = 0
        self.opened_at = None

    def allow(self, now: float) -> bool:
        """Return True if a call may proceed right now (and flip OPEN→HALF-OPEN if the cooldown passed)."""
        # YOUR CODE HERE
        return False

    def on_success(self) -> None:
        """A call succeeded: reset to CLOSED."""
        # YOUR CODE HERE
        return None

    def on_failure(self, now: float) -> None:
        """A call failed: count it; trip OPEN at the threshold, or immediately if HALF-OPEN."""
        # YOUR CODE HERE
        return None
