"""Everything in one file. Don't edit — restructure it into careerpilot_core/."""

import argparse
from collections import Counter
from dataclasses import dataclass

VERSION = "0.1.0"


@dataclass(frozen=True)
class JobListing:
    title: str
    skills: frozenset[str]

    @classmethod
    def parse(cls, text: str) -> "JobListing":
        title, _, skills = text.partition(":")
        return cls(title.strip(), frozenset(s.strip().lower() for s in skills.split(",") if s.strip()))


def top_skills(jobs: list[JobListing], n: int) -> list[tuple[str, int]]:
    counts = Counter(skill for job in jobs for skill in job.skills)
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:n]


def format_report(jobs: list[JobListing], n: int) -> str:
    lines = [f"Top skills across {len(jobs)} job(s):"]
    lines += [f"{rank}. {skill} ({count})" for rank, (skill, count) in enumerate(top_skills(jobs, n), start=1)]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="careerpilot_core")
    parser.add_argument("--version", action="store_true")
    sub = parser.add_subparsers(dest="command")
    report = sub.add_parser("report")
    report.add_argument("jobs", nargs="+")
    report.add_argument("--top", type=int, default=5)
    args = parser.parse_args(argv)
    if args.version:
        print(VERSION)
        return 0
    if args.command == "report":
        print(format_report([JobListing.parse(text) for text in args.jobs], args.top))
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
