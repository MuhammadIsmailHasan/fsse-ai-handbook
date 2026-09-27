"""Find services that write to tables they don't own. See README.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Service:
    name: str
    owns: tuple[str, ...]
    writes: tuple[str, ...]


def find_ownership_violations(services: list[Service]) -> list[str]:
    raise NotImplementedError
