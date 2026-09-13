"""Turn a Locust *_stats.csv file into answers: which endpoints break our SLOs? See README.md."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EndpointStats:
    method: str
    name: str
    requests: int
    failures: int
    median_ms: float
    p95_ms: float
    rps: float

    @property
    def failure_rate(self) -> float:
        raise NotImplementedError


def load_stats(path: str | Path) -> list[EndpointStats]:
    raise NotImplementedError


def slo_violations(stats: list[EndpointStats], max_p95_ms: float, max_failure_rate: float) -> list[str]:
    raise NotImplementedError


def slowest(stats: list[EndpointStats], n: int = 3) -> list[str]:
    raise NotImplementedError
