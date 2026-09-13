import argparse
import sys

from hexajobs.application.use_cases import import_jobs, recommend_jobs


def main(argv=None, stream=sys.stdout):
    parser = argparse.ArgumentParser(prog="hexajobs")
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("recommend")
    rec.add_argument("--feed", required=True)
    rec.add_argument("--email", required=True)
    rec.add_argument("--skills", required=True)
    rec.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args(argv)
    stream.write(f"Imported {import_jobs(args.feed)} jobs\n")
    recommend_jobs(args.email, args.skills.split(","), stream, args.threshold)
    return 0
