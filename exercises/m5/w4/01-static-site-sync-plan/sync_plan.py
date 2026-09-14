"""Static site deploy planner. See README.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Upload:
    key: str
    content_type: str
    cache_control: str


@dataclass(frozen=True)
class Plan:
    uploads: list[Upload]
    deletes: list[str]
    invalidations: list[str]


def cache_control(path: str) -> str:
    raise NotImplementedError


def content_type(path: str) -> str:
    raise NotImplementedError


def plan(local: dict[str, bytes], remote: dict[str, str], *, delete: bool = True) -> Plan:
    raise NotImplementedError
