"""Turn a Locust *_stats.csv file into answers: which endpoints break our SLOs?"""

import csv
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
        return self.failures / self.requests if self.requests else 0.0


def _number(value: str) -> float:
    return 0.0 if value in ("", "N/A") else float(value)


def load_stats(path: str | Path) -> list[EndpointStats]:
    with open(path, newline="") as file:
        return [
            EndpointStats(
                method=row["Type"],
                name=row["Name"],
                requests=int(row["Request Count"]),
                failures=int(row["Failure Count"]),
                median_ms=_number(row["Median Response Time"]),
                p95_ms=_number(row["95%"]),
                rps=_number(row["Requests/s"]),
            )
            for row in csv.DictReader(file)
            if row["Name"] != "Aggregated" and int(row["Request Count"]) > 0
        ]


def slo_violations(stats: list[EndpointStats], max_p95_ms: float, max_failure_rate: float) -> list[str]:
    messages = []
    for stat in sorted(stats, key=lambda s: s.name):
        if stat.p95_ms > max_p95_ms:
            messages.append(f"{stat.name}: p95 {stat.p95_ms:.0f}ms > {max_p95_ms:.0f}ms")
        if stat.failure_rate > max_failure_rate:
            messages.append(f"{stat.name}: failure rate {stat.failure_rate:.1%} > {max_failure_rate:.1%}")
    return messages


def slowest(stats: list[EndpointStats], n: int = 3) -> list[str]:
    return [s.name for s in sorted(stats, key=lambda s: (-s.p95_ms, s.name))[:n]]
