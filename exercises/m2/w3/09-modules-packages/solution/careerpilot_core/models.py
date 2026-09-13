"""Data models. Imports nothing from the rest of the package (lowest layer)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobListing:
    title: str
    skills: frozenset[str]

    @classmethod
    def parse(cls, text: str) -> "JobListing":
        title, _, skills = text.partition(":")
        return cls(title.strip(), frozenset(s.strip().lower() for s in skills.split(",") if s.strip()))
