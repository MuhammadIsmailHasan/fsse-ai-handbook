"""Reference solution."""

import functools
import time
from collections import deque


def timed(records: list, clock=time.perf_counter):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                records.append((func.__name__, clock() - start))

        return wrapper

    return decorator


def retry(times: int, exceptions: tuple[type[BaseException], ...] = (Exception,)):
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise

        return wrapper

    return decorator


def make_rate_limiter(max_calls: int, per_seconds: float, clock=time.monotonic):
    calls: deque[float] = deque()  # timestamps of allowed calls, oldest first

    def allow() -> bool:
        now = clock()
        while calls and now - calls[0] >= per_seconds:
            calls.popleft()
        if len(calls) < max_calls:
            calls.append(now)
            return True
        return False

    return allow


class Router:
    def __init__(self):
        self._routes: dict[tuple[str, str], object] = {}

    def route(self, method: str, path: str):
        key = (method.upper(), path)

        def decorator(func):
            if key in self._routes:
                raise ValueError(f"Route already registered: {key}")
            self._routes[key] = func
            return func

        return decorator

    def dispatch(self, method: str, path: str, *args, **kwargs):
        try:
            handler = self._routes[(method.upper(), path)]
        except KeyError:
            raise LookupError(f"No route for {method.upper()} {path}") from None
        return handler(*args, **kwargs)
