"""SOLID exporter — reference solution.

S: each class has one reason to change (a format, or a place to write).
O: new formats/destinations are new classes; export_applications never changes.
L: every Exporter returns a str for any list (including empty); every Destination stores content under a name.
I: two small protocols instead of one "ExportManager" interface.
D: export_applications depends on the protocols, not on concrete classes.
"""

import csv
import io
import json
from pathlib import Path
from typing import Protocol

FIELDS = ("company", "role", "status", "applied_on")


class Exporter(Protocol):
    extension: str

    def render(self, applications: list[dict]) -> str: ...


class Destination(Protocol):
    def write(self, filename: str, content: str) -> None: ...


def _row(application: dict) -> dict:
    applied_on = application.get("applied_on")
    return {
        "company": application["company"],
        "role": application["role"],
        "status": application["status"],
        "applied_on": applied_on.isoformat() if applied_on else None,
    }


class CsvExporter:
    extension = "csv"

    def render(self, applications: list[dict]) -> str:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for application in applications:
            row = _row(application)
            writer.writerow({**row, "applied_on": row["applied_on"] or ""})
        return buffer.getvalue()


class JsonExporter:
    extension = "json"

    def render(self, applications: list[dict]) -> str:
        return json.dumps([_row(a) for a in applications], indent=2)


class MarkdownExporter:
    extension = "md"

    def render(self, applications: list[dict]) -> str:
        lines = ["| Company | Role | Status | Applied on |", "|---|---|---|---|"]
        for application in applications:
            row = _row(application)
            lines.append(f"| {row['company']} | {row['role']} | {row['status']} | {row['applied_on'] or ''} |")
        return "\n".join(lines) + "\n"


class FolderDestination:
    def __init__(self, folder: str | Path):
        self.folder = Path(folder)

    def write(self, filename: str, content: str) -> None:
        (self.folder / filename).write_text(content, encoding="utf-8")


class MemoryDestination:
    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def write(self, filename: str, content: str) -> None:
        self.files[filename] = content


def export_applications(applications: list[dict], exporter: Exporter, destination: Destination, basename: str = "applications") -> str:
    filename = f"{basename}.{exporter.extension}"
    destination.write(filename, exporter.render(applications))
    return filename
