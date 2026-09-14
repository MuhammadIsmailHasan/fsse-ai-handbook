"""DORA metrics. See README.md."""

from dataclasses import dataclass
from datetime import datetime
from statistics import median


@dataclass(frozen=True)
class Deployment:
    id: str
    environment: str
    deployed_at: datetime
    commits: list[datetime]
    outcome: str


@dataclass(frozen=True)
class Incident:
    id: str
    deployment_id: str
    started_at: datetime
    resolved_at: datetime | None


def _production(deployments: list[Deployment]) -> list[Deployment]:
    return [d for d in deployments if d.environment == "production"]


def _hours(delta) -> float:
    return delta.total_seconds() / 3600


def deployment_frequency(deployments: list[Deployment], start: datetime, end: datetime) -> float:
    count = sum(1 for d in _production(deployments) if d.outcome == "success" and start <= d.deployed_at < end)
    weeks = (end - start).total_seconds() / (7 * 24 * 3600)
    return round(count / weeks, 2)


def lead_time_hours(deployments: list[Deployment]) -> float | None:
    durations = [_hours(d.deployed_at - commit) for d in _production(deployments) if d.outcome == "success" for commit in d.commits]
    return round(median(durations), 1) if durations else None


def change_failure_rate(deployments: list[Deployment], incidents: list[Incident]) -> float | None:
    production = _production(deployments)
    if not production:
        return None
    with_incidents = {incident.deployment_id for incident in incidents}
    failures = sum(1 for d in production if d.outcome in ("failed", "rolled_back") or d.id in with_incidents)
    return round(failures / len(production), 3)


def recovery_time_hours(incidents: list[Incident], deployments: list[Deployment]) -> float | None:
    production_ids = {d.id for d in _production(deployments)}
    durations = [_hours(i.resolved_at - i.started_at) for i in incidents if i.resolved_at is not None and i.deployment_id in production_ids]
    return round(median(durations), 1) if durations else None


LEVELS = ["elite", "high", "medium", "low"]


def classify(frequency_per_week: float | None, lead_time_hours: float | None, failure_rate: float | None, recovery_hours: float | None) -> str:
    def level(value, checks):
        if value is None:
            return 0
        for index, passes in enumerate(checks):
            if passes(value):
                return index
        return 3

    levels = [
        level(frequency_per_week, [lambda v: v >= 7, lambda v: v >= 1, lambda v: v >= 0.25]),
        level(lead_time_hours, [lambda v: v < 24, lambda v: v < 168, lambda v: v < 720]),
        level(failure_rate, [lambda v: v <= 0.05, lambda v: v <= 0.10, lambda v: v <= 0.15]),
        level(recovery_hours, [lambda v: v < 1, lambda v: v < 24, lambda v: v < 168]),
    ]
    return LEVELS[max(levels)]  # a team is only as good as its weakest metric
