"""Blue/green deploys on a single Docker host. See README.md."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Result:
    ok: bool
    active: str | None
    message: str


def deploy(
    image: str,
    *,
    state_dir: Path,
    runner: Callable[[list[str], dict[str, str]], int],
    is_healthy: Callable[[str], bool],
    attempts: int = 20,
    wait: float = 3,
    drain: float = 10,
    sleep: Callable[[float], None] = time.sleep,
) -> Result:
    raise NotImplementedError
