"""Checks your resolution of the conflict lab. Don't edit this file."""

import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

LAB = Path(__file__).parent / "conflict-lab"
pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is required")


def git(*args):
    return subprocess.run(["git", "-C", str(LAB), *args], capture_output=True, text=True).stdout.strip()


@pytest.fixture(scope="module", autouse=True)
def lab_exists():
    assert (LAB / ".git").is_dir(), "Run: bash make_conflict.sh"


def test_merge_is_finished():
    assert not (LAB / ".git" / "MERGE_HEAD").exists(), "Finish the merge: git add … && git commit --no-edit"
    assert git("status", "--porcelain") == "", "Commit all resolved files"
    parents = git("log", "-1", "--format=%P").split()
    assert len(parents) == 2, "The last commit should be the merge commit (two parents)"


def test_no_conflict_markers():
    for name in ("pricing.py", "CHANGELOG.md"):
        text = (LAB / name).read_text()
        for marker in ("<<<<<<<", "=======", ">>>>>>>"):
            assert marker not in text, f"Conflict marker {marker} left in {name}"


def test_both_behaviors_kept():
    spec = importlib.util.spec_from_file_location("lab_pricing", LAB / "pricing.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.final_price(100_000, False) == 111_000
    assert module.final_price(100_000, True) == 99_900


def test_changelog_keeps_both_entries():
    text = (LAB / "CHANGELOG.md").read_text()
    assert "10% discount" in text and "11% tax" in text
