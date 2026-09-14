"""Cost estimation, credit runway and waste detection. See README.md."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Estimate:
    lines: list[tuple[str, float]]
    total: float


@dataclass(frozen=True)
class Runway:
    credits_exhausted: date | None
    plan_ends: date
    account_closes: date
    reason: str


@dataclass(frozen=True)
class Waste:
    resource_id: str
    issue: str
    monthly_cost: float


def monthly_cost(resources: list[dict], prices: dict) -> Estimate:
    raise NotImplementedError


def credit_runway(credits: float, monthly_cost: float, opened: date, today: date) -> Runway:
    raise NotImplementedError


def budget_alerts(monthly_budget: float) -> list[tuple[str, float]]:
    raise NotImplementedError


def find_waste(inventory: list[dict], prices: dict) -> list[Waste]:
    raise NotImplementedError
