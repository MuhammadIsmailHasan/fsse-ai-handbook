"""Redis patterns. See README.md."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import redis


class InProgressError(Exception):
    """Another request with the same idempotency key is still running."""


def cache_aside(r: redis.Redis, key: str, ttl: int, loader: Callable[[], Any], *, jitter: float = 0.1, rng: Callable[[], float] = random.random) -> Any:
    raise NotImplementedError


def invalidate(r: redis.Redis, *keys: str) -> int:
    raise NotImplementedError


def cache_with_lock(r: redis.Redis, key: str, ttl: int, loader: Callable[[], Any], *, lock_ttl_ms: int = 5000, poll_interval: float = 0.02, max_wait: float = 2.0) -> Any:
    raise NotImplementedError


class SlidingWindowRateLimiter:
    def __init__(self, r: redis.Redis, *, limit: int, window_seconds: float, prefix: str = "ratelimit", clock: Callable[[], float] = time.time):
        raise NotImplementedError

    def allow(self, identity: str) -> tuple[bool, float]:
        raise NotImplementedError


@dataclass(frozen=True)
class Job:
    id: str
    payload: dict
    raw: str


class ReliableQueue:
    def __init__(self, r: redis.Redis, name: str, *, clock: Callable[[], float] = time.time):
        raise NotImplementedError

    def enqueue(self, payload: dict) -> str:
        raise NotImplementedError

    def reserve(self, timeout: float = 1.0) -> Job | None:
        raise NotImplementedError

    def ack(self, job: Job) -> None:
        raise NotImplementedError

    def requeue_stale(self, older_than: float) -> int:
        raise NotImplementedError

    def ready_count(self) -> int:
        raise NotImplementedError

    def processing_count(self) -> int:
        raise NotImplementedError


def run_once(r: redis.Redis, key: str, ttl: int, action: Callable[[], Any]) -> tuple[Any, bool]:
    raise NotImplementedError
