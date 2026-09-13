"""Grades YOUR tests (test_discounts.py) — you don't need to edit this file.

1. Your tests must PASS against the correct discounts.py.
2. For each file in mutants/ (a copy of discounts.py with ONE bug), your tests must FAIL.
A mutant that passes your tests "survived": a behavior you didn't check.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
MUTANTS = sorted((HERE / "mutants").glob("m*.py"))


def run_learner_tests(tmp_path: Path, implementation: Path) -> subprocess.CompletedProcess[str]:
    shutil.copy(implementation, tmp_path / "discounts.py")
    shutil.copy(HERE / "test_discounts.py", tmp_path / "test_discounts.py")
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(tmp_path), "-q", "-p", "no:cacheprovider", "--rootdir", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_your_tests_pass_on_the_correct_code(tmp_path):
    result = run_learner_tests(tmp_path, HERE / "discounts.py")
    assert result.returncode == 0, "Your tests must pass on the correct discounts.py:\n" + result.stdout[-2000:]


@pytest.mark.parametrize("mutant", MUTANTS, ids=[m.stem for m in MUTANTS])
def test_your_tests_kill_mutant(tmp_path, mutant):
    result = run_learner_tests(tmp_path, mutant)
    # returncode 1 = some tests failed (killed). 0 = all passed (survived). Others = collection/usage errors.
    assert result.returncode != 0, f"Mutant {mutant.stem} SURVIVED — your tests don't check this behavior yet."
    assert result.returncode == 1, "Your test file errored instead of failing:\n" + result.stdout[-2000:]
