"""GitHub OIDC trust policies for AWS. See README.md."""

import re
from urllib.parse import urlsplit

PROVIDER_HOST = "token.actions.githubusercontent.com"
ACTION = "sts:AssumeRoleWithWebIdentity"


def _check_name(kind: str, value: str) -> None:
    if not value or any(char in value for char in "*?:"):
        raise ValueError(f"invalid {kind}: {value!r}")


def trust_policy(account_id: str, owner: str, repo: str, *, environments=(), branches=()) -> dict:
    if not re.fullmatch(r"\d{12}", account_id):
        raise ValueError("account_id must be 12 digits")
    _check_name("owner", owner)
    _check_name("repo", repo)
    if not environments and not branches:
        raise ValueError("restrict the role to specific environments or branches")
    for name in environments:
        _check_name("environment", name)
    for name in branches:
        _check_name("branch", name)

    subjects = [f"repo:{owner}/{repo}:environment:{env}" for env in environments]
    subjects += [f"repo:{owner}/{repo}:ref:refs/heads/{branch}" for branch in branches]
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Federated": f"arn:aws:iam::{account_id}:oidc-provider/{PROVIDER_HOST}"},
                "Action": ACTION,
                "Condition": {
                    "StringEquals": {f"{PROVIDER_HOST}:aud": "sts.amazonaws.com"},
                    "StringLike": {f"{PROVIDER_HOST}:sub": subjects},
                },
            }
        ],
    }


def _as_list(value) -> list[str]:
    return value if isinstance(value, list) else [value]


def _like(pattern: str, value: str) -> bool:
    regex = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in pattern)
    return re.fullmatch(regex, value, flags=re.DOTALL) is not None


OPERATORS = {
    "StringEquals": lambda expected, actual: actual == expected,
    "StringLike": _like,
}


def _statement_allows(statement: dict, claims: dict[str, str]) -> bool:
    if statement.get("Effect") != "Allow" or ACTION not in _as_list(statement.get("Action", [])):
        return False
    issuer_host = urlsplit(claims.get("iss", "")).hostname or ""
    federated = _as_list(statement.get("Principal", {}).get("Federated", []))
    if not issuer_host or not any(arn.endswith(f"oidc-provider/{issuer_host}") for arn in federated):
        return False
    for operator, conditions in statement.get("Condition", {}).items():
        compare = OPERATORS.get(operator)
        if compare is None:
            return False  # fail closed on anything we don't understand
        for key, expected in conditions.items():
            claim = key.split(":", 1)[1] if ":" in key else key
            actual = claims.get(claim)
            if actual is None or not any(compare(pattern, actual) for pattern in _as_list(expected)):
                return False
    return True


def allows(policy: dict, claims: dict[str, str]) -> bool:
    return any(_statement_allows(statement, claims) for statement in _as_list(policy.get("Statement", [])))
