"""Reference solution. See README.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Service:
    name: str
    owns: tuple[str, ...]
    writes: tuple[str, ...]


def find_ownership_violations(services: list[Service]) -> list[str]:
    # One owner per table.
    owner_of: dict[str, str] = {}
    for service in services:
        for table in service.owns:
            owner_of[table] = service.name

    # A write to a table owned by someone else is a violation.
    violations: list[str] = []
    for service in services:
        for table in service.writes:
            owner = owner_of.get(table)
            if owner is not None and owner != service.name:
                violations.append(f"{service.name} writes to {table} owned by {owner}")

    return sorted(violations)
