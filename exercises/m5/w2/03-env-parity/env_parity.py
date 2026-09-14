"""Environment parity checker. See README.md."""

import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    environment: str
    key: str
    code: str
    message: str


def parse_env(text: str) -> dict[str, str]:
    raise NotImplementedError


def check(environments: dict[str, dict[str, str]], *, required: set[str]) -> list[Issue]:
    raise NotImplementedError


def main(argv: list[str]) -> int:
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
