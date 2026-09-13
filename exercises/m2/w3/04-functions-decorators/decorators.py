"""M2 · W3 · 04 — Build your own decorators."""

import functools  # noqa: F401
import time


def timed(records: list, clock=time.perf_counter):
    # YOUR CODE HERE
    def decorator(func):
        return func

    return decorator


def retry(times: int, exceptions: tuple[type[BaseException], ...] = (Exception,)):
    # YOUR CODE HERE
    def decorator(func):
        return func

    return decorator


def make_rate_limiter(max_calls: int, per_seconds: float, clock=time.monotonic):
    # YOUR CODE HERE
    def allow() -> bool:
        return True

    return allow


class Router:
    # YOUR CODE HERE
    def route(self, method: str, path: str):
        def decorator(func):
            return func

        return decorator

    def dispatch(self, method: str, path: str, *args, **kwargs):
        raise LookupError(path)
