"""Runtime behavior + mypy --strict for service.py. Don't edit this file."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import service

HERE = Path(__file__).parent


class FakeRepo:
    def __init__(self):
        self.rows = {
            1: {"id": 1, "company": "Kopi Data", "status": "applied", "salary": 12_000_000},
            2: {"id": 2, "company": "Lintas AI", "status": "interview", "salary": None},
        }
        self.saved = []

    def get(self, application_id):
        return self.rows.get(application_id)

    def save(self, application):
        self.saved.append(application)
        self.rows[application["id"]] = application


def test_first_or_none():
    assert service.first_or_none([3, 4]) == 3
    assert service.first_or_none([]) is None


def test_salary_label():
    repo = FakeRepo()
    assert service.salary_label(repo, 1) == "Rp 12.000.000"
    assert service.salary_label(repo, 2) == "Not disclosed"
    with pytest.raises(LookupError):
        service.salary_label(repo, 99)


def test_advance():
    repo = FakeRepo()
    updated = service.advance(repo, 1, "interview")
    assert updated["status"] == "interview"
    assert repo.saved == [updated]
    with pytest.raises(LookupError):
        service.advance(repo, 99, "offer")


def test_mypy_strict_passes():
    source = (HERE / "service.py").read_text()
    for required in ("Literal", "TypedDict", "Protocol"):
        assert required in source, f"Use {required} in service.py"
    mypy = [sys.executable, "-m", "mypy"]
    if shutil.which("mypy") is None:
        pytest.importorskip("mypy")
    result = subprocess.run(
        [*mypy, "--strict", "--no-incremental", "--python-version", "3.12", str(HERE / "service.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout
