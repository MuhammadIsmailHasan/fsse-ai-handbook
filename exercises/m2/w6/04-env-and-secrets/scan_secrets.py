"""A tiny secret scanner (real projects: gitleaks / GitHub secret scanning). See README.md."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str


def scan_text(text: str, path: str) -> list[Finding]:
    raise NotImplementedError


def scan_directory(root: str | Path) -> list[Finding]:
    raise NotImplementedError
