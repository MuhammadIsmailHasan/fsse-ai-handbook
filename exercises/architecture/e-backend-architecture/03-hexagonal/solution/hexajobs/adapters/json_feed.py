"""Driven adapter: a JSON file implements the JobFeed port."""

import json
from pathlib import Path

from hexajobs.domain.model import JobPosting


class JsonFileFeed:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def fetch_jobs(self) -> list[JobPosting]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            JobPosting(item["id"], item["title"], item["company"], item.get("salary_max"), tuple(s.lower() for s in item["skills"]))
            for item in data
        ]
