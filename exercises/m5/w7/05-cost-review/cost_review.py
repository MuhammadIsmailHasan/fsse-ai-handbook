"""Review cloud costs and find idle resources. See README.md."""

from dataclasses import dataclass

HOURS_PER_MONTH = 730


@dataclass(frozen=True)
class Resource:
    name: str
    hourly_cost: float
    in_use: bool


def monthly_cost(resources: list[Resource]) -> float:
    raise NotImplementedError


def idle_resources(resources: list[Resource]) -> list[str]:
    raise NotImplementedError
