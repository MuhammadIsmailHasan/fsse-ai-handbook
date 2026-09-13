import ast
import io
import json
import typing
from pathlib import Path

import pytest

PACKAGE = Path(__file__).parent / "hexajobs"
IO_MODULES = {"json", "os", "pathlib", "sys", "io", "sqlite3", "requests", "flask", "sqlalchemy"}
ALLOWED_INTERNAL = {
    "domain": {"hexajobs.domain"},
    "application": {"hexajobs.domain", "hexajobs.application"},
    "adapters": {"hexajobs.domain", "hexajobs.application", "hexajobs.adapters"},
}


def imports_of(path):
    modules = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            modules |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


@pytest.mark.parametrize("layer", ["domain", "application", "adapters"])
def test_dependency_rule(layer):
    for path in (PACKAGE / layer).glob("*.py"):
        for module in imports_of(path):
            if module.startswith("hexajobs"):
                assert any(module == allowed or module.startswith(allowed + ".") for allowed in ALLOWED_INTERNAL[layer]), f"{path.name} ({layer}) imports {module}"
            elif layer in ("domain", "application"):
                assert module.split(".")[0] not in IO_MODULES, f"{path.name} ({layer}) does I/O via {module}"


def test_ports_are_protocols():
    from hexajobs.application import ports

    for name, methods in {"JobFeed": {"fetch_jobs"}, "JobStore": {"save_all", "all"}, "Notifier": {"notify"}}.items():
        port = getattr(ports, name)
        assert getattr(port, "_is_protocol", False), f"{name} should be a typing.Protocol"
        assert methods <= set(dir(port))


def job(id, skills, title="Dev", company="Kopi"):
    from hexajobs.domain.model import JobPosting

    return JobPosting(id, title, company, None, tuple(skills))


class FakeFeed:
    def __init__(self, jobs):
        self.jobs = jobs

    def fetch_jobs(self):
        return list(self.jobs)


class FakeStore:
    def __init__(self):
        self.jobs = []

    def save_all(self, jobs):
        self.jobs.extend(jobs)

    def all(self):
        return list(self.jobs)


class FakeNotifier:
    def __init__(self):
        self.calls = []

    def notify(self, email, jobs):
        self.calls.append((email, [j.id for j in jobs]))


def test_match_score():
    from hexajobs.domain.model import match_score

    assert match_score(job("a", ["python", "sql"]), ["SQL"]) == 0.5
    assert match_score(job("b", []), ["python"]) == 0.0


def test_import_jobs_with_fakes():
    from hexajobs.application.use_cases import ImportJobs

    store = FakeStore()
    feed = FakeFeed([job("a", ["python"]), job("b", ["go"]), job("a", ["python"])])
    assert ImportJobs(feed, store)() == 2
    assert ImportJobs(feed, store)() == 0
    assert [j.id for j in store.all()] == ["a", "b"]


def test_recommend_jobs_with_fakes():
    from hexajobs.application.use_cases import RecommendJobs

    store, notifier = FakeStore(), FakeNotifier()
    store.save_all([job("c", ["python", "sql"]), job("a", ["python", "aws", "sql", "docker"]), job("b", ["python"]), job("d", ["go"])])
    result = RecommendJobs(store, notifier)("siti@example.com", ["Python", "sql"])
    assert [j.id for j in result] == ["b", "c", "a"]
    assert notifier.calls == [("siti@example.com", ["b", "c", "a"])]
    assert RecommendJobs(store, notifier)("siti@example.com", ["rust"]) == [] and len(notifier.calls) == 1


def test_adapters(tmp_path):
    from hexajobs.adapters.console_notifier import ConsoleNotifier
    from hexajobs.adapters.json_feed import JsonFileFeed
    from hexajobs.adapters.memory_store import InMemoryJobStore

    path = tmp_path / "jobs.json"
    path.write_text(json.dumps([{"id": "k-1", "title": "Backend Engineer", "company": "Kopi Data", "skills": ["Python", "SQL"]}]))
    jobs = JsonFileFeed(path).fetch_jobs()
    assert jobs == [job("k-1", ["python", "sql"], "Backend Engineer", "Kopi Data")]
    store = InMemoryJobStore()
    store.save_all(jobs)
    assert store.all() == jobs
    out = io.StringIO()
    ConsoleNotifier(out).notify("a@b.id", jobs)
    assert out.getvalue() == "To a@b.id: 1 job(s)\n- Backend Engineer at Kopi Data\n"


def test_cli_end_to_end(tmp_path):
    from hexajobs.entrypoints.cli import main

    path = tmp_path / "jobs.json"
    path.write_text(json.dumps([
        {"id": "k-2", "title": "Data Analyst", "company": "Awan", "skills": ["sql", "excel"]},
        {"id": "k-1", "title": "Backend Engineer", "company": "Kopi Data", "salary_max": 15000000, "skills": ["python", "sql"]},
        {"id": "k-3", "title": "Go Dev", "company": "Batik", "skills": ["go"]},
    ]))
    out = io.StringIO()
    assert main(["recommend", "--feed", str(path), "--email", "siti@example.com", "--skills", "python,sql"], stream=out) == 0
    assert out.getvalue() == "Imported 3 jobs\nTo siti@example.com: 2 job(s)\n- Backend Engineer at Kopi Data\n- Data Analyst at Awan\n"
