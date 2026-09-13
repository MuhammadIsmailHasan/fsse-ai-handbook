"""Entry point for `python -m careerpilot_core`."""

import argparse

from . import __version__
from .formatting import format_report
from .models import JobListing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="careerpilot_core")
    parser.add_argument("--version", action="store_true", help="print the version and exit")
    sub = parser.add_subparsers(dest="command")
    report = sub.add_parser("report", help="show top skills")
    report.add_argument("jobs", nargs="+", help='jobs as "Title:skill1,skill2"')
    report.add_argument("--top", type=int, default=5)
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0
    if args.command == "report":
        print(format_report([JobListing.parse(text) for text in args.jobs], args.top))
        return 0
    parser.print_help()
    return 1


raise SystemExit(main())
