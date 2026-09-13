"""Grades YOUR integration tests (test_api.py) — you don't need to edit this file.

1. Your tests must PASS against the correct api.py.
2. For each file in mutants/ (api.py with ONE bug), your tests must FAIL.
Needs the exercise database:  cd exercises && docker compose up -d
"""

import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

HERE = Path(__file__).parent
MUTANTS = sorted((HERE / "mutants").glob("m*.py"))


def exercises_root() -> Path:
    # Runs go inside exercises/ so the shared conftest.py (pg_url fixture) is available.
    return next(p for p in HERE.parents if (p / "pyproject.toml").exists())


@pytest.fixture
def workdir():
    path = exercises_root() / ".grader-tmp" / uuid.uuid4().hex[:10]
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def run_learner_tests(workdir: Path, implementation: Path) -> subprocess.CompletedProcess[str]:
    for name in ("app.py", "models.py", "test_api.py"):
        shutil.copy(HERE / name, workdir / name)
    if (HERE / "conftest.py").exists():
        shutil.copy(HERE / "conftest.py", workdir / "conftest.py")
    shutil.copy(implementation, workdir / "api.py")
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(workdir), "-q", "-p", "no:cacheprovider"],
        cwd=exercises_root(),
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_your_tests_pass_on_the_correct_api(workdir):
    result = run_learner_tests(workdir, HERE / "api.py")
    assert result.returncode == 0, "Your tests must pass on the correct api.py:\n" + result.stdout[-2500:]


@pytest.mark.parametrize("mutant", MUTANTS, ids=[m.stem for m in MUTANTS])
def test_your_tests_kill_mutant(workdir, mutant):
    result = run_learner_tests(workdir, mutant)
    assert result.returncode != 0, f"Mutant {mutant.stem} SURVIVED — your tests don't check this behavior yet."
    assert result.returncode == 1, "Your tests errored instead of failing:\n" + result.stdout[-2500:]
