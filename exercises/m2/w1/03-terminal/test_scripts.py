"""Runs your bash scripts on temporary folders. Don't edit this file."""

import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).parent
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="bash is required")


def run(script, *args):
    return subprocess.run([BASH, str(HERE / script), *map(str, args)], capture_output=True, text=True)


# ---- organize.sh -------------------------------------------------------------


def test_organize_moves_files(tmp_path):
    for name in ["app.log", "error log.log", "jobs.csv", "config.json", "logo.png", "photo.jpg", "notes.txt"]:
        (tmp_path / name).write_text("x")

    result = run("organize.sh", tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Moved 6 file(s)"
    assert sorted(p.name for p in (tmp_path / "logs").iterdir()) == ["app.log", "error log.log"]
    assert sorted(p.name for p in (tmp_path / "data").iterdir()) == ["config.json", "jobs.csv"]
    assert sorted(p.name for p in (tmp_path / "images").iterdir()) == ["logo.png", "photo.jpg"]
    assert (tmp_path / "notes.txt").exists()


def test_organize_only_creates_needed_folders(tmp_path):
    (tmp_path / "only.log").write_text("x")
    result = run("organize.sh", tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "logs").is_dir()
    assert not (tmp_path / "data").exists() and not (tmp_path / "images").exists()


def test_organize_empty_folder(tmp_path):
    result = run("organize.sh", tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Moved 0 file(s)"


def test_organize_errors(tmp_path):
    missing = tmp_path / "nope"
    result = run("organize.sh", missing)
    assert result.returncode == 1
    assert f"Error: not a directory: {missing}" in result.stderr
    assert run("organize.sh").returncode != 0


# ---- error_report.sh ---------------------------------------------------------

LOG = """2026-09-13T10:02:11 INFO GET /api/jobs 200 34ms
2026-09-13T10:02:12 ERROR POST /api/applications 500 120ms
2026-09-13T10:03:40 ERROR GET /api/jobs 500 80ms
2026-09-13T10:04:01 WARN GET /api/jobs 429 5ms
2026-09-13T10:05:22 ERROR POST /api/applications 500 131ms
2026-09-13T10:06:09 INFO POST /api/applications 201 60ms
2026-09-13T10:07:15 ERROR POST /api/applications 502 90ms
"""


def test_error_report(tmp_path):
    log = tmp_path / "app.log"
    log.write_text(LOG)
    result = run("error_report.sh", log)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "Errors: 4",
        "Top failing endpoints:",
        "3 POST /api/applications",
        "1 GET /api/jobs",
    ]


def test_error_report_limits_to_three_and_breaks_ties(tmp_path):
    lines = [
        "t ERROR GET /d 500 1ms",
        "t ERROR GET /c 500 1ms",
        "t ERROR GET /b 500 1ms",
        "t ERROR GET /a 500 1ms",
        "t ERROR GET /a 500 1ms",
    ]
    log = tmp_path / "app.log"
    log.write_text("\n".join(lines) + "\n")
    result = run("error_report.sh", log)
    assert result.stdout.splitlines()[2:] == ["2 GET /a", "1 GET /b", "1 GET /c"]


def test_error_report_no_errors(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("t INFO GET / 200 1ms\n")
    result = run("error_report.sh", log)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["Errors: 0", "Top failing endpoints:"]


def test_error_report_missing_file(tmp_path):
    result = run("error_report.sh", tmp_path / "missing.log")
    assert result.returncode == 1
    assert "Error: file not found:" in result.stderr
