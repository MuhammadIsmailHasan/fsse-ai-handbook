"""SOLID exporter. See README.md."""

from pathlib import Path
from typing import Protocol


class Exporter(Protocol):
    extension: str

    def render(self, applications: list[dict]) -> str: ...


class Destination(Protocol):
    def write(self, filename: str, content: str) -> None: ...


# TODO: CsvExporter, JsonExporter, MarkdownExporter, FolderDestination, MemoryDestination


def export_applications(applications: list[dict], exporter: Exporter, destination: Destination, basename: str = "applications") -> str:
    raise NotImplementedError
