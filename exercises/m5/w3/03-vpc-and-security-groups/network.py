"""VPC planning and security-group analysis. See README.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Subnet:
    name: str
    tier: str
    az: str
    cidr: str


def plan_subnets(vpc_cidr: str, azs: list[str], *, tiers: tuple[str, ...] = ("public", "app", "data"), prefix: int = 24) -> list[Subnet]:
    raise NotImplementedError


def usable_ips(cidr: str) -> int:
    raise NotImplementedError


def route_problems(subnets: list[Subnet], route_tables: dict[str, dict[str, str]]) -> list[str]:
    raise NotImplementedError


def can_reach(groups: dict, members: dict, source: str, target: str, port: int, protocol: str = "tcp") -> bool:
    raise NotImplementedError


def audit(groups: dict) -> list[tuple[str, str]]:
    raise NotImplementedError
