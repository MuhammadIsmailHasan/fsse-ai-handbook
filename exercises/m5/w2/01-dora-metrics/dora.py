"""DORA metrics. See README.md."""

from dataclasses import dataclass
from datetime import datetime


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


def deployment_frequency(deployments: list[Deployment], start: datetime, end: datetime) -> float:
    raise NotImplementedError


def lead_time_hours(deployments: list[Deployment]) -> float | None:
    raise NotImplementedError


def change_failure_rate(deployments: list[Deployment], incidents: list[Incident]) -> float | None:
    raise NotImplementedError


def recovery_time_hours(incidents: list[Incident], deployments: list[Deployment]) -> float | None:
    raise NotImplementedError


def classify(frequency_per_week: float | None, lead_time_hours: float | None, failure_rate: float | None, recovery_hours: float | None) -> str:
    raise NotImplementedError
