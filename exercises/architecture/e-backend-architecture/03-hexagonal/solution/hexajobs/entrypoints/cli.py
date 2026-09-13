"""Driving adapter + composition root: parse the command line, wire adapters into use cases, run."""

import argparse
import sys

from hexajobs.adapters.console_notifier import ConsoleNotifier
from hexajobs.adapters.json_feed import JsonFileFeed
from hexajobs.adapters.memory_store import InMemoryJobStore
from hexajobs.application.use_cases import ImportJobs, RecommendJobs


def main(argv=None, stream=sys.stdout):
    parser = argparse.ArgumentParser(prog="hexajobs")
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("recommend")
    rec.add_argument("--feed", required=True)
    rec.add_argument("--email", required=True)
    rec.add_argument("--skills", required=True)
    rec.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args(argv)

    store = InMemoryJobStore()
    imported = ImportJobs(JsonFileFeed(args.feed), store)()
    stream.write(f"Imported {imported} jobs\n")
    RecommendJobs(store, ConsoleNotifier(stream))(args.email, args.skills.split(","), args.threshold)
    return 0
