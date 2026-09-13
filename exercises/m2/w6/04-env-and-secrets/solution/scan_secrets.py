"""A tiny secret scanner (real projects: gitleaks / GitHub secret scanning). Learning version."""

import re
from dataclasses import dataclass
from pathlib import Path

PATTERNS = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\b(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,})\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
ASSIGNMENT = re.compile(
    # name (optionally quoted) = or : value (optionally quoted); unquoted values followed by "(" are function calls
    r"""(?i)\b\w*(?:secret|password|passwd|token|api_key|apikey)\w*\b['"]?\s*[:=]\s*(?P<quote>['"]?)(?P<value>[^'"\s#,()]++)(?P=quote)(?!\()"""
)
PLACEHOLDER = re.compile(r"(?i)^(?:change[-_]?me|changeme|your[-_].*|xxx+|\*+|<.*>|\$\{.*\}|\$\w+|none|null|test|example.*|dummy.*)$")
CODE_LOOKUP = re.compile(r"(?i)(?:os\.environ|getenv|environ\.get|config\[|settings\.)")
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str


def scan_text(text: str, path: str) -> list[Finding]:
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        kinds = [kind for kind, pattern in PATTERNS.items() if pattern.search(line)]
        if not kinds and not CODE_LOOKUP.search(line):
            for match in ASSIGNMENT.finditer(line):
                value = match.group("value")
                if len(value) >= 8 and not PLACEHOLDER.match(value):
                    kinds.append("hardcoded_secret")
                    break
        findings.extend(Finding(path, number, kind) for kind in kinds)
    return findings


def scan_directory(root: str | Path) -> list[Finding]:
    root = Path(root)
    findings = []
    for file in sorted(root.rglob("*")):
        relative = file.relative_to(root)
        if not file.is_file() or SKIP_DIRS.intersection(relative.parts):
            continue
        if file.name == ".env" or (file.name.startswith(".env.") and not file.name.endswith(".example")):
            findings.append(Finding(relative.as_posix(), 0, "env_file"))
            continue
        try:
            text = file.read_text()
        except UnicodeDecodeError:
            continue
        findings.extend(scan_text(text, relative.as_posix()))
    return findings
