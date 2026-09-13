import ast
import csv
import io
import json
from datetime import date
from pathlib import Path

import pytest

import solid_export as se

APPS = [
    {"company": "Kopi Data", "role": "Backend Engineer", "status": "applied", "applied_on": date(2026, 9, 2)},
    {"company": "Awan, Cloud & Co", "role": "Data Analyst", "status": "saved", "applied_on": None},
]


def test_csv_quotes_commas_and_handles_none():
    content = se.CsvExporter().render(APPS)
    assert se.CsvExporter.extension == "csv"
    assert content.splitlines()[0] == "company,role,status,applied_on"
    assert list(csv.DictReader(io.StringIO(content))) == [
        {"company": "Kopi Data", "role": "Backend Engineer", "status": "applied", "applied_on": "2026-09-02"},
        {"company": "Awan, Cloud & Co", "role": "Data Analyst", "status": "saved", "applied_on": ""},
    ]
    assert "\r" not in content


def test_json():
    content = se.JsonExporter().render(APPS)
    assert se.JsonExporter.extension == "json"
    assert json.loads(content) == [
        {"company": "Kopi Data", "role": "Backend Engineer", "status": "applied", "applied_on": "2026-09-02"},
        {"company": "Awan, Cloud & Co", "role": "Data Analyst", "status": "saved", "applied_on": None},
    ]
    assert content == json.dumps(json.loads(content), indent=2)
    assert list(json.loads(content)[0]) == ["company", "role", "status", "applied_on"]


def test_markdown():
    assert se.MarkdownExporter.extension == "md"
    assert se.MarkdownExporter().render(APPS) == (
        "| Company | Role | Status | Applied on |\n"
        "|---|---|---|---|\n"
        "| Kopi Data | Backend Engineer | applied | 2026-09-02 |\n"
        "| Awan, Cloud & Co | Data Analyst | saved |  |\n"
    )


@pytest.mark.parametrize("exporter_class", ["CsvExporter", "JsonExporter", "MarkdownExporter"])
def test_every_exporter_honors_the_contract_for_empty_lists(exporter_class):
    content = getattr(se, exporter_class)().render([])
    assert isinstance(content, str) and content


def test_destinations(tmp_path):
    folder = se.FolderDestination(tmp_path)
    folder.write("a.txt", "halo ✨")
    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == "halo ✨"
    memory = se.MemoryDestination()
    memory.write("b.txt", "x")
    assert memory.files == {"b.txt": "x"}


def test_export_applications_wires_exporter_and_destination():
    memory = se.MemoryDestination()
    assert se.export_applications(APPS, se.JsonExporter(), memory, basename="september") == "september.json"
    assert json.loads(memory.files["september.json"])[0]["company"] == "Kopi Data"


def test_open_for_extension_closed_for_modification(tmp_path):
    class HtmlExporter:  # a brand-new format, defined outside your module
        extension = "html"

        def render(self, applications):
            return "<ul>" + "".join(f"<li>{a['company']}</li>" for a in applications) + "</ul>"

    filename = se.export_applications(APPS, HtmlExporter(), se.FolderDestination(tmp_path))
    assert (tmp_path / filename).read_text() == "<ul><li>Kopi Data</li><li>Awan, Cloud &amp; Co</li></ul>".replace("&amp;", "&")


def test_export_function_depends_on_abstractions_only():
    tree = ast.parse(Path(se.__file__).read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "export_applications")
    names = {n.id for n in ast.walk(function) if isinstance(n, ast.Name)}
    concrete = {"CsvExporter", "JsonExporter", "MarkdownExporter", "FolderDestination", "MemoryDestination", "open", "isinstance"}
    assert not names & concrete, f"export_applications should not know concrete classes: {names & concrete}"
