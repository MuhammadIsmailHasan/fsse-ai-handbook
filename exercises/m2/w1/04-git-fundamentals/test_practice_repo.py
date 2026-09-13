"""Inspects the Git history in ./practice. Don't edit this file."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent / "practice"
CONVENTIONAL = re.compile(r"^(feat|fix|docs|test|refactor|chore|style)(\([\w\-./]+\))?!?: \S.*$")
pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is required")


def git(*args):
    result = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    return result.stdout.strip()


@pytest.fixture(scope="module", autouse=True)
def repo_exists():
    assert (REPO / ".git").is_dir(), "Create the practice repo: mkdir practice && cd practice && git init -b main"


def subjects():
    return git("log", "main", "--format=%s").splitlines()


def test_on_main_with_enough_commits():
    assert git("branch", "--show-current") == "main"
    assert len(subjects()) >= 6, "Follow the whole story (at least 6 commits on main)"


def test_messages_are_conventional():
    for subject in subjects():
        if subject.startswith(("Merge branch", "Revert \"")):
            continue
        assert CONVENTIONAL.match(subject), f"Not a Conventional Commit: {subject!r}"


def test_gitignore_protects_env():
    tracked = git("ls-files").splitlines()
    assert ".gitignore" in tracked
    ignore = (REPO / ".gitignore").read_text()
    assert ".env" in ignore and "__pycache__" in ignore
    assert (REPO / ".env").exists(), "Create the .env file (it should exist locally)"
    assert ".env" not in tracked, ".env must not be committed"
    assert "API_KEY" not in git("log", "-p", "--all"), "A secret appears in the history!"


def test_feature_branch_merged():
    branches = git("branch", "--all", "--format=%(refname:short)").splitlines()
    merged_features = [b for b in git("branch", "--merged", "main", "--format=%(refname:short)").splitlines() if b.startswith("feature/")]
    reflog_mentions = "feature/" in git("reflog", "--all")
    assert merged_features or (reflog_mentions and not any(b.startswith("feature/") for b in branches)), (
        "Create a feature/... branch and merge it into main"
    )
    assert "def farewell" in (REPO / "app.py").read_text()
    assert (REPO / "README.md").exists()


def test_revert_was_used():
    assert any(s.startswith("Revert \"") for s in subjects()), "Undo a commit with `git revert`"


def test_annotated_tag_on_main():
    assert "v0.1.0" in git("tag").splitlines(), "Create the v0.1.0 tag"
    assert git("cat-file", "-t", "v0.1.0") == "tag", "Use an annotated tag: git tag -a v0.1.0 -m '...'"
    assert git("rev-list", "-n", "1", "v0.1.0") == git("rev-parse", "main"), "Tag the latest main commit"


def test_working_tree_clean():
    assert git("status", "--porcelain") == "", "Commit or ignore all changes"
