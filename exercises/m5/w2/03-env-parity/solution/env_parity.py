"""Environment parity checker. See README.md."""

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Issue:
    environment: str
    key: str
    code: str
    message: str


LINE = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def _unquote(raw: str, number: int) -> str:
    raw = raw.strip()
    if raw.startswith("'"):
        end = raw.find("'", 1)
        if end == -1:
            raise ValueError(f"line {number}: unterminated single quote")
        return raw[1:end]
    if raw.startswith('"'):
        out, i = [], 1
        while i < len(raw):
            char = raw[i]
            if char == "\\" and i + 1 < len(raw):
                out.append({"n": "\n", '"': '"', "\\": "\\"}.get(raw[i + 1], "\\" + raw[i + 1]))
                i += 2
                continue
            if char == '"':
                return "".join(out)
            out.append(char)
            i += 1
        raise ValueError(f"line {number}: unterminated double quote")
    return re.split(r"\s+#", raw, maxsplit=1)[0].strip()


def parse_env(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = LINE.match(stripped)
        if not match:
            raise ValueError(f"line {number}: expected KEY=value")
        values[match.group(1)] = _unquote(match.group(2), number)
    return values


SECRET_WORDS = ("SECRET", "PASSWORD", "TOKEN", "PRIVATE_KEY")
PLACEHOLDERS = ("change", "replace", "example", "xxx")
TRUTHY = {"1", "true", "yes", "on"}


def _is_secret(key: str) -> bool:
    return any(word in key for word in SECRET_WORDS) and not key.endswith("_CLIENT_KEY")


def check(environments: dict[str, dict[str, str]], *, required: set[str]) -> list[Issue]:
    issues: list[Issue] = []
    all_keys = set().union(*(env.keys() for env in environments.values())) if environments else set()

    for name, env in environments.items():
        for key in sorted(required):
            if not env.get(key):
                issues.append(Issue(name, key, "MISSING", f"{key} is required"))
        for key in sorted(all_keys - set(env) - required):
            issues.append(Issue(name, key, "DRIFT", f"{key} exists in other environments but not in {name}"))

        if name in ("staging", "production"):
            for key, value in env.items():
                if _is_secret(key) and value and (len(value) < 32 or any(p in value.lower() for p in PLACEHOLDERS)):
                    issues.append(Issue(name, key, "WEAK_SECRET", f"{key} looks like a placeholder or is shorter than 32 characters"))

        if name == "production":
            for key in ("DEBUG", "FLASK_DEBUG"):
                if env.get(key, "").strip().lower() in TRUTHY:
                    issues.append(Issue(name, key, "DEBUG_IN_PRODUCTION", f"{key} must be off in production"))
            for key, value in env.items():
                if "localhost" in value or "127.0.0.1" in value:
                    issues.append(Issue(name, key, "LOCALHOST_IN_PRODUCTION", f"{key} points to localhost"))
                if value.startswith("SB-Mid-"):
                    issues.append(Issue(name, key, "SANDBOX_IN_PRODUCTION", f"{key} is a Midtrans sandbox key"))
            if env.get("MIDTRANS_IS_PRODUCTION", "").lower() != "true":
                issues.append(Issue(name, "MIDTRANS_IS_PRODUCTION", "SANDBOX_IN_PRODUCTION", "Midtrans must use production mode"))

    staging, production = environments.get("staging"), environments.get("production")
    if staging is not None and production is not None:
        for key, value in production.items():
            if _is_secret(key) and value and staging.get(key) == value:
                issues.append(Issue("production", key, "SHARED_SECRET", f"{key} is identical in staging and production"))

    return sorted(issues, key=lambda issue: (issue.environment, issue.key, issue.code))


def main(argv: list[str]) -> int:
    required: set[str] = set()
    environments: dict[str, dict[str, str]] = {}
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg == "--require":
            required = {key.strip() for key in args.pop(0).split(",") if key.strip()}
        else:
            name, _, path = arg.partition("=")
            environments[name] = parse_env(Path(path).read_text())
    issues = check(environments, required=required)
    for issue in issues:
        print(f"{issue.environment} {issue.key} {issue.code}: {issue.message}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
