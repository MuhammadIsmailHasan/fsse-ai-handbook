"""Reference solution. See README.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    span_id: str
    service: str
    duration_ms: int


def slowest_step(spans: list[Span]) -> str | None:
    best: Span | None = None
    for span in spans:
        # Strictly greater, so the FIRST span wins a tie.
        if best is None or span.duration_ms > best.duration_ms:
            best = span
    return best.span_id if best is not None else None


def time_by_service(spans: list[Span]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for span in spans:
        totals[span.service] = totals.get(span.service, 0) + span.duration_ms
    return totals
