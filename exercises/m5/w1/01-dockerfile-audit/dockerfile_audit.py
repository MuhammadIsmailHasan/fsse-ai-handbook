"""A tiny Dockerfile linter. See README.md."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Instruction:
    line: int
    keyword: str
    args: str


@dataclass(frozen=True)
class Finding:
    rule: str
    line: int
    severity: Literal["error", "warning"]
    message: str


def parse(text: str) -> list[Instruction]:
    raise NotImplementedError


def audit(text: str) -> list[Finding]:
    raise NotImplementedError


def main(argv: list[str]) -> int:
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
