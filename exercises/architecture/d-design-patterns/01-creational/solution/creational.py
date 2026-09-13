"""Factory, Builder and a safe Singleton — reference solution."""

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache

# ---------- Factory with a registry ----------

EXPORTERS: dict[str, type] = {}


def register_exporter(name: str):
    def decorator(cls: type) -> type:
        if name in EXPORTERS:
            raise ValueError(f"exporter {name!r} is already registered")
        EXPORTERS[name] = cls
        return cls

    return decorator


def create_exporter(name: str, **options):
    try:
        cls = EXPORTERS[name]
    except KeyError:
        raise ValueError(f"unknown exporter {name!r} (available: {', '.join(sorted(EXPORTERS))})") from None
    return cls(**options)


@register_exporter("csv")
class CsvLinesExporter:
    def __init__(self, separator: str = ","):
        self.separator = separator

    def render(self, rows: list[dict]) -> str:
        return "\n".join(self.separator.join(str(v) for v in row.values()) for row in rows)


@register_exporter("json")
class JsonLinesExporter:
    def render(self, rows: list[dict]) -> str:
        return "\n".join(json.dumps(row) for row in rows)


# ---------- Builder ----------


@dataclass(frozen=True)
class JobPosting:
    title: str
    company: str
    city: str | None
    remote: bool
    salary_min: int | None
    salary_max: int | None
    skills: tuple[str, ...]


class JobPostingBuilder:
    def __init__(self) -> None:
        self._title: str | None = None
        self._company: str | None = None
        self._city: str | None = None
        self._remote = False
        self._salary: tuple[int | None, int | None] = (None, None)
        self._skills: list[str] = []

    def titled(self, title: str) -> "JobPostingBuilder":
        self._title = title
        return self

    def at(self, company: str) -> "JobPostingBuilder":
        self._company = company
        return self

    def in_city(self, city: str) -> "JobPostingBuilder":
        self._city = city
        return self

    def remote(self) -> "JobPostingBuilder":
        self._remote = True
        return self

    def salary(self, minimum: int | None, maximum: int | None) -> "JobPostingBuilder":
        self._salary = (minimum, maximum)
        return self

    def requires(self, *skills: str) -> "JobPostingBuilder":
        for skill in skills:
            cleaned = skill.strip().lower()
            if cleaned and cleaned not in self._skills:
                self._skills.append(cleaned)
        return self

    def build(self) -> JobPosting:
        missing = sorted(name for name, value in (("title", self._title), ("company", self._company)) if not value)
        if missing:
            raise ValueError(f"missing: {', '.join(missing)}")
        if not self._city and not self._remote:
            raise ValueError("city or remote required")
        low, high = self._salary
        if low is not None and high is not None and low > high:
            raise ValueError("salary_min must be <= salary_max")
        return JobPosting(self._title, self._company, self._city, self._remote, low, high, tuple(self._skills))  # type: ignore[arg-type]


# ---------- Singleton, the testable way ----------


@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str


def load_settings(env: Mapping[str, str]) -> Settings:
    database_url = env.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is required")
    return Settings(env.get("APP_ENV", "development"), database_url)


@cache
def get_settings() -> Settings:
    """One shared instance per process — but created lazily and resettable with get_settings.cache_clear()."""
    return load_settings(os.environ)
