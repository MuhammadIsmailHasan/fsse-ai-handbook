"""A simplified IAM identity-policy evaluator and reviewer. See README.md."""

from dataclasses import dataclass
from typing import Literal

Decision = Literal["Allow", "ExplicitDeny", "ImplicitDeny"]


@dataclass(frozen=True)
class Finding:
    sid: str
    severity: Literal["high", "medium"]
    message: str


def evaluate(policies: list[dict], action: str, resource: str, context: dict | None = None) -> Decision:
    raise NotImplementedError


def review(policy: dict) -> list[Finding]:
    raise NotImplementedError
