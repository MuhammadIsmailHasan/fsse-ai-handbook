"""A tiny Dockerfile linter. See README.md."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
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
    instructions: list[Instruction] = []
    buffer: list[str] = []
    start = 0
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue  # also skips comment lines inside a continuation
        if not buffer:
            start = number
        continued = line.endswith("\\")
        buffer.append(line[:-1].strip() if continued else line)
        if continued:
            continue
        joined = " ".join(part for part in buffer if part)
        keyword, _, args = joined.partition(" ")
        instructions.append(Instruction(start, keyword.upper(), args.strip()))
        buffer = []
    if buffer:  # file ended in the middle of a continuation
        joined = " ".join(part for part in buffer if part)
        keyword, _, args = joined.partition(" ")
        instructions.append(Instruction(start, keyword.upper(), args.strip()))
    return instructions


def _split_stages(instructions: list[Instruction]) -> list[list[Instruction]]:
    stages: list[list[Instruction]] = []
    for instruction in instructions:
        if instruction.keyword == "FROM":
            stages.append([])
        if stages:
            stages[-1].append(instruction)
    return stages


def _from_parts(args: str) -> tuple[str, str | None]:
    tokens = [token for token in args.split() if not token.startswith("--")]
    image = tokens[0] if tokens else ""
    name = tokens[2].lower() if len(tokens) >= 3 and tokens[1].lower() == "as" else None
    return image, name


SECRET_WORDS = ("SECRET", "PASSWORD", "TOKEN", "API_KEY", "PRIVATE_KEY")
INSTALL_PATTERN = re.compile(r"\b(pip3? install|uv sync|npm ci|npm install|poetry install)\b")


def _defined_with_values(keyword: str, args: str) -> list[str]:
    """Variable names that get a value in an ENV/ARG instruction."""
    if keyword == "ARG":
        name, sep, _ = args.partition("=")
        return [name.strip()] if sep else []
    if "=" not in args.split(" ", 1)[0]:  # legacy form: ENV NAME value
        name, _, value = args.partition(" ")
        return [name] if value.strip() else []
    return [pair.split("=", 1)[0] for pair in re.findall(r"(\w+=(?:\"[^\"]*\"|'[^']*'|\S+))", args)]


def audit(text: str) -> list[Finding]:
    findings: list[Finding] = []
    stages = _split_stages(parse(text))
    stage_names: set[str] = set()

    for index, stage in enumerate(stages):
        first = stage[0]
        image, name = _from_parts(first.args)
        base = image.lower()
        is_stage_ref = base in stage_names
        if not is_stage_ref and base != "scratch" and "@sha256:" not in base:
            last_segment = base.rsplit("/", 1)[-1]
            if ":" not in last_segment or last_segment.endswith(":latest"):
                findings.append(Finding("DF001", first.line, "error", f"Pin the base image version instead of '{image}'"))
        if name:
            stage_names.add(name)

        copied_everything = False
        for instruction in stage[1:]:
            kw, args = instruction.keyword, instruction.args
            if kw in ("CMD", "ENTRYPOINT") and not args.startswith("["):
                findings.append(Finding("DF003", instruction.line, "error", f"Use exec form for {kw} so signals reach your process"))
            if kw in ("COPY", "ADD"):
                sources = [token for token in args.split() if not token.startswith("--")][:-1]
                if any(source in (".", "./") for source in sources):
                    copied_everything = True
                if kw == "ADD" and any(source.startswith(("http://", "https://")) for source in sources):
                    findings.append(Finding("DF007", instruction.line, "warning", "Download with RUN curl + checksum instead of ADD <url>"))
            if kw == "RUN":
                if copied_everything and INSTALL_PATTERN.search(args):
                    findings.append(Finding("DF004", instruction.line, "warning", "Install dependencies before copying the whole project to keep the layer cache"))
                if "apt-get install" in args and ("--no-install-recommends" not in args or "rm -rf /var/lib/apt/lists" not in args):
                    findings.append(Finding("DF005", instruction.line, "warning", "Use --no-install-recommends and clean /var/lib/apt/lists in the same RUN"))
            if kw in ("ENV", "ARG"):
                for variable in _defined_with_values(kw, args):
                    if any(word in variable.upper() for word in SECRET_WORDS):
                        findings.append(Finding("DF006", instruction.line, "error", f"Don't bake secrets into the image ({variable}); pass them at runtime"))

        if index == len(stages) - 1:
            users = [instruction for instruction in stage if instruction.keyword == "USER"]
            if not users:
                findings.append(Finding("DF002", first.line, "error", "Final stage runs as root; add a non-root USER"))
            elif users[-1].args.split(":")[0] in ("root", "0"):
                findings.append(Finding("DF002", users[-1].line, "error", "Final stage runs as root; add a non-root USER"))
            if not any(instruction.keyword == "HEALTHCHECK" for instruction in stage):
                findings.append(Finding("DF008", first.line, "warning", "Add a HEALTHCHECK (or document the orchestrator's health check)"))

    return sorted(findings, key=lambda finding: (finding.line, finding.rule))


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: dockerfile_audit.py <Dockerfile>", file=sys.stderr)
        return 2
    path = Path(argv[0])
    findings = audit(path.read_text())
    for finding in findings:
        print(f"{path.name}:{finding.line} {finding.rule} {finding.severity}: {finding.message}")
    errors = sum(finding.severity == "error" for finding in findings)
    warnings = len(findings) - errors
    print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
