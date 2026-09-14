"""Lambda handlers for expiring unpaid payments. See README.md."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Deps:
    repository: Any
    sqs: Any
    queue_url: str
    clock: Callable[[], datetime]


def scan_handler(event: dict, context: Any, deps: Deps) -> dict:
    raise NotImplementedError


def expire_handler(event: dict, context: Any, deps: Deps) -> dict:
    raise NotImplementedError
