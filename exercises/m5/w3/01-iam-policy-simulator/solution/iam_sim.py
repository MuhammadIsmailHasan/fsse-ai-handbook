"""A simplified IAM identity-policy evaluator and reviewer. See README.md."""

import ipaddress
import re
from dataclasses import dataclass
from typing import Literal

Decision = Literal["Allow", "ExplicitDeny", "ImplicitDeny"]


@dataclass(frozen=True)
class Finding:
    sid: str
    severity: Literal["high", "medium"]
    message: str


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _wildcard(pattern: str, value: str, *, ignore_case: bool) -> bool:
    regex = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in pattern)
    return re.fullmatch(regex, value, flags=re.IGNORECASE | re.DOTALL if ignore_case else re.DOTALL) is not None


def _matches(statement: dict, key: str, not_key: str, value: str, *, ignore_case: bool) -> bool:
    if key in statement:
        return any(_wildcard(p, value, ignore_case=ignore_case) for p in _as_list(statement[key]))
    if not_key in statement:
        return not any(_wildcard(p, value, ignore_case=ignore_case) for p in _as_list(statement[not_key]))
    return False


def _bool(value) -> str:
    return str(value).lower()


def _compare(operator: str, expected: list, actual) -> bool:
    if operator == "StringEquals":
        return any(str(actual) == str(e) for e in expected)
    if operator == "StringNotEquals":
        return all(str(actual) != str(e) for e in expected)
    if operator == "StringLike":
        return any(_wildcard(str(e), str(actual), ignore_case=False) for e in expected)
    if operator == "Bool":
        return any(_bool(actual) == _bool(e) for e in expected)
    if operator == "NumericLessThan":
        return any(float(actual) < float(e) for e in expected)
    if operator == "NumericGreaterThanEquals":
        return any(float(actual) >= float(e) for e in expected)
    if operator == "IpAddress":
        return any(ipaddress.ip_address(str(actual)) in ipaddress.ip_network(str(e), strict=False) for e in expected)
    raise KeyError(operator)


def _conditions_pass(statement: dict, context: dict) -> bool:
    lowered = {k.lower(): v for k, v in context.items()}
    for operator, conditions in statement.get("Condition", {}).items():
        if_exists = operator.endswith("IfExists")
        base = operator.removesuffix("IfExists")
        for key, expected in conditions.items():
            if key.lower() not in lowered:
                if if_exists:
                    continue
                return False
            try:
                if not _compare(base, _as_list(expected), lowered[key.lower()]):
                    return False
            except KeyError:
                return False  # unknown operator: the statement doesn't apply
    return True


def evaluate(policies: list[dict], action: str, resource: str, context: dict | None = None) -> Decision:
    context = context or {}
    allowed = False
    for policy in policies:
        for statement in _as_list(policy.get("Statement")):
            applies = (
                _matches(statement, "Action", "NotAction", action, ignore_case=True)
                and _matches(statement, "Resource", "NotResource", resource, ignore_case=False)
                and _conditions_pass(statement, context)
            )
            if not applies:
                continue
            if statement.get("Effect") == "Deny":
                return "ExplicitDeny"  # deny always wins
            if statement.get("Effect") == "Allow":
                allowed = True
    return "Allow" if allowed else "ImplicitDeny"


READ_ONLY = re.compile(r"^[a-z0-9-]+:(Describe|List|Get)", re.IGNORECASE)


def review(policy: dict) -> list[Finding]:
    findings: list[Finding] = []
    for index, statement in enumerate(_as_list(policy.get("Statement"))):
        if statement.get("Effect") != "Allow":
            continue
        sid = statement.get("Sid") or f"#{index}"
        actions = [a for a in _as_list(statement.get("Action"))]
        resources = _as_list(statement.get("Resource"))
        if "*" in actions:
            findings.append(Finding(sid, "high", "Action '*' grants full administrator access"))
        if "*" in resources and any(a.lower() in ("iam:passrole", "iam:*") for a in actions):
            findings.append(Finding(sid, "high", "iam:PassRole on every role allows privilege escalation"))
        if "NotAction" in statement:
            findings.append(Finding(sid, "high", "Allow with NotAction grants everything else, including future services"))
        service_wildcards = [a for a in actions if a != "*" and a.endswith(":*")]
        if service_wildcards:
            findings.append(Finding(sid, "medium", f"service-wide wildcard: {', '.join(service_wildcards)}"))
        if "*" in resources and any(a != "*" and not READ_ONLY.match(a) for a in actions):
            findings.append(Finding(sid, "medium", "write actions on Resource '*'; scope to specific ARNs"))
    return findings
