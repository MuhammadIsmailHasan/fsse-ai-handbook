"""Tests for decorators.py. Don't edit this file."""

import pytest

from decorators import Router, make_rate_limiter, retry, timed


class FakeClock:
    def __init__(self, now=0.0):
        self.now = now

    def __call__(self):
        return self.now


# ---- timed -------------------------------------------------------------------


def test_timed_records_and_returns():
    clock = FakeClock()
    records = []

    @timed(records, clock=clock)
    def work(a, b=0):
        """Adds numbers."""
        clock.now += 1.5
        return a + b

    assert work(2, b=3) == 5
    assert records == [("work", 1.5)]
    assert work.__name__ == "work" and work.__doc__ == "Adds numbers."


def test_timed_records_even_when_raising():
    clock = FakeClock()
    records = []

    @timed(records, clock=clock)
    def boom():
        clock.now += 0.25
        raise KeyError("x")

    with pytest.raises(KeyError):
        boom()
    assert records == [("boom", 0.25)]


# ---- retry -------------------------------------------------------------------


def test_retry_succeeds_after_failures():
    calls = []

    @retry(times=3, exceptions=(ConnectionError,))
    def flaky(value):
        calls.append(value)
        if len(calls) < 3:
            raise ConnectionError("down")
        return f"ok {value}"

    assert flaky("x") == "ok x"
    assert len(calls) == 3
    assert flaky.__name__ == "flaky"


def test_retry_reraises_last_exception():
    calls = []

    @retry(times=2, exceptions=(ConnectionError,))
    def always_down():
        calls.append(1)
        raise ConnectionError(f"attempt {len(calls)}")

    with pytest.raises(ConnectionError, match="attempt 2"):
        always_down()
    assert len(calls) == 2


def test_retry_does_not_retry_other_exceptions():
    calls = []

    @retry(times=5, exceptions=(ConnectionError,))
    def bug():
        calls.append(1)
        raise ValueError("bug")

    with pytest.raises(ValueError):
        bug()
    assert len(calls) == 1


def test_retry_validates_times():
    with pytest.raises(ValueError):
        retry(times=0)


# ---- rate limiter --------------------------------------------------------------


def test_rate_limiter_sliding_window():
    clock = FakeClock()
    allow = make_rate_limiter(max_calls=2, per_seconds=10, clock=clock)
    assert allow() and allow()
    assert not allow()
    clock.now = 9.9
    assert not allow()
    clock.now = 10.0          # the first two calls (at t=0) are now outside the window
    assert allow() and allow()
    assert not allow()


def test_rate_limiters_are_independent():
    clock = FakeClock()
    a = make_rate_limiter(1, 60, clock=clock)
    b = make_rate_limiter(1, 60, clock=clock)
    assert a() and b()
    assert not a() and not b()


# ---- router ------------------------------------------------------------------


def test_router_registers_and_dispatches():
    router = Router()

    @router.route("GET", "/jobs/<id>")
    def get_job(job_id):
        return {"id": job_id}

    assert get_job(7) == {"id": 7}                      # function returned unchanged
    assert router.dispatch("get", "/jobs/<id>", 7) == {"id": 7}


def test_router_unknown_and_duplicate_routes():
    router = Router()

    @router.route("POST", "/applications")
    def create():
        return "created"

    with pytest.raises(LookupError):
        router.dispatch("GET", "/applications")
    with pytest.raises(ValueError):

        @router.route("post", "/applications")
        def create_again():
            return "again"


def test_routers_do_not_share_routes():
    first, second = Router(), Router()

    @first.route("GET", "/health")
    def health():
        return "ok"

    with pytest.raises(LookupError):
        second.dispatch("GET", "/health")
