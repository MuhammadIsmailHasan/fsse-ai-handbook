import ast
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import creational as c


# ---------- factory ----------

def test_registered_exporters():
    assert c.EXPORTERS["csv"] is c.CsvLinesExporter and c.EXPORTERS["json"] is c.JsonLinesExporter
    rows = [{"company": "Kopi Data", "role": "Dev"}, {"company": "Awan", "role": "QA"}]
    assert c.create_exporter("csv").render(rows) == "Kopi Data,Dev\nAwan,QA"
    assert c.create_exporter("csv", separator=";").render(rows) == "Kopi Data;Dev\nAwan;QA"
    assert c.create_exporter("json").render(rows) == '{"company": "Kopi Data", "role": "Dev"}\n{"company": "Awan", "role": "QA"}'


def test_unknown_exporter_lists_available_names():
    with pytest.raises(ValueError) as error:
        c.create_exporter("xlsx")
    assert str(error.value) == "unknown exporter 'xlsx' (available: csv, json)"


def test_registry_is_extensible_and_rejects_duplicates():
    @c.register_exporter("upper")
    class UpperExporter:
        def render(self, rows):
            return str(rows).upper()

    try:
        assert UpperExporter.__name__ == "UpperExporter", "the decorator must return the class"
        assert c.create_exporter("upper").render(["a"]) == "['A']"
        with pytest.raises(ValueError):
            c.register_exporter("upper")(UpperExporter)
    finally:
        c.EXPORTERS.pop("upper", None)


# ---------- builder ----------

def test_builder_chains_and_builds_frozen_posting():
    builder = c.JobPostingBuilder()
    assert builder.titled("Backend Engineer") is builder
    posting = builder.at("Kopi Data").in_city("Jakarta").salary(9_000_000, 14_000_000).requires(" Python", "SQL", "python ").requires("Docker").build()
    assert posting == c.JobPosting("Backend Engineer", "Kopi Data", "Jakarta", False, 9_000_000, 14_000_000, ("python", "sql", "docker"))
    with pytest.raises(FrozenInstanceError):
        posting.title = "changed"


def test_remote_posting_without_city():
    posting = c.JobPostingBuilder().titled("AI Engineer").at("Lintas AI").remote().build()
    assert posting.remote is True and posting.city is None and posting.skills == () and posting.salary_min is None


@pytest.mark.parametrize(
    ("configure", "message"),
    [
        (lambda b: b.in_city("Bandung"), "missing: company, title"),
        (lambda b: b.titled("QA").in_city("Bandung"), "missing: company"),
        (lambda b: b.titled("QA").at("Batik Soft"), "city or remote required"),
        (lambda b: b.titled("QA").at("Batik Soft").remote().salary(10, 5), "salary_min must be <= salary_max"),
    ],
)
def test_builder_validation(configure, message):
    with pytest.raises(ValueError) as error:
        configure(c.JobPostingBuilder()).build()
    assert str(error.value) == message


def test_built_postings_are_independent_of_later_builder_changes():
    builder = c.JobPostingBuilder().titled("Dev").at("Kopi").remote().requires("python")
    first = builder.build()
    second = builder.build()
    builder.requires("go").titled("Senior Dev")
    assert first == second and first.skills == ("python",) and first.title == "Dev"


# ---------- singleton ----------

def test_load_settings_is_pure():
    assert c.load_settings({"DATABASE_URL": "postgresql://x"}) == c.Settings("development", "postgresql://x")
    assert c.load_settings({"DATABASE_URL": "postgresql://y", "APP_ENV": "production"}).app_env == "production"
    with pytest.raises(ValueError):
        c.load_settings({})


def test_get_settings_is_cached_and_resettable(monkeypatch):
    c.get_settings.cache_clear()
    monkeypatch.setenv("DATABASE_URL", "postgresql://first")
    first = c.get_settings()
    monkeypatch.setenv("DATABASE_URL", "postgresql://second")
    assert c.get_settings() is first, "one shared instance"
    c.get_settings.cache_clear()
    assert c.get_settings().database_url == "postgresql://second", "tests can reset it"
    c.get_settings.cache_clear()


def test_no_settings_created_at_import_time():
    tree = ast.parse(Path(c.__file__).read_text())
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr)):
            calls = {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            assert not calls & {"Settings", "load_settings", "get_settings"}, "don't build settings at import time"
