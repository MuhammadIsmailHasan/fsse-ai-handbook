"""Read a trace: find the slowest span and total time per service. See README.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    span_id: str
    service: str
    duration_ms: int


def slowest_step(spans: list[Span]) -> str | None:
    raise NotImplementedError


def time_by_service(spans: list[Span]) -> dict[str, int]:
    raise NotImplementedError
