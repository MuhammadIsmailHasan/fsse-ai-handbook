"""Reference solution. See README.md."""

from dataclasses import dataclass

HOURS_PER_MONTH = 730


@dataclass(frozen=True)
class Resource:
    name: str
    hourly_cost: float
    in_use: bool


def monthly_cost(resources: list[Resource]) -> float:
    total = sum(r.hourly_cost * HOURS_PER_MONTH for r in resources)
    return round(total, 2)


def idle_resources(resources: list[Resource]) -> list[str]:
    return sorted(r.name for r in resources if not r.in_use)
