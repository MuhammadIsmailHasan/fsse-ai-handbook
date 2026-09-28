from resilience import CircuitBreaker, backoff_delay


def test_backoff_doubles_and_caps():
    assert backoff_delay(0, base=0.5, cap=30) == 0.5
    assert backoff_delay(1, base=0.5, cap=30) == 1.0
    assert backoff_delay(2, base=0.5, cap=30) == 2.0
    assert backoff_delay(3, base=0.5, cap=30) == 4.0
    # Cap kicks in for large attempts.
    assert backoff_delay(20, base=0.5, cap=30) == 30


def test_breaker_starts_closed_and_allows():
    cb = CircuitBreaker(failure_threshold=3, cooldown=10)
    assert cb.state == "closed"
    assert cb.allow(now=0) is True


def test_breaker_opens_after_threshold_failures():
    cb = CircuitBreaker(failure_threshold=3, cooldown=10)
    cb.on_failure(now=0)
    cb.on_failure(now=1)
    assert cb.state == "closed"  # not yet at threshold
    cb.on_failure(now=2)
    assert cb.state == "open"
    # While open (before cooldown) calls are blocked — fail fast.
    assert cb.allow(now=3) is False


def test_open_then_half_open_then_recover():
    cb = CircuitBreaker(failure_threshold=2, cooldown=10)
    cb.on_failure(now=0)
    cb.on_failure(now=0)
    assert cb.state == "open"
    assert cb.allow(now=5) is False          # still cooling down
    assert cb.allow(now=10) is True          # cooldown passed → half-open trial
    assert cb.state == "half-open"
    cb.on_success()                          # trial worked
    assert cb.state == "closed"
    assert cb.allow(now=11) is True


def test_half_open_failure_reopens():
    cb = CircuitBreaker(failure_threshold=2, cooldown=10)
    cb.on_failure(now=0)
    cb.on_failure(now=0)
    cb.allow(now=10)                         # → half-open
    assert cb.state == "half-open"
    cb.on_failure(now=10)                    # trial failed → open again
    assert cb.state == "open"
    assert cb.allow(now=15) is False         # cooling down again
    assert cb.allow(now=20) is True          # next cooldown → half-open
