"""Checks for workflows/ci.yml, workflows/dependabot.yml and junit_summary.py. Don't edit this file."""

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from junit_summary import FailedTest, Report, annotations, markdown_summary, parse_report

HERE = Path(__file__).parent
SHA_PIN = re.compile(r"^[\w.-]+/[\w.-]+(/[\w./-]+)?@[0-9a-f]{40}$")


# ---------- junit_summary.py ----------

def sample():
    return (HERE / "sample-report.xml").read_text()


def test_parse_real_pytest_report():
    report = parse_report(sample())
    assert (report.total, report.failures, report.errors, report.skipped, report.passed) == (5, 1, 1, 1, 2)
    assert report.duration == pytest.approx(0.028)
    assert report.failed_tests == [
        FailedTest("tests.test_orders::test_discount_rounds_down", "AssertionError: discount must round down"),
        FailedTest("tests.test_orders::test_saves_order", 'failed on setup with "ConnectionError: could not connect to server: Connection refused'),
    ]


def test_parse_sums_multiple_suites_and_bare_testsuite_root():
    two = """<testsuites>
      <testsuite name="a" tests="2" failures="0" errors="0" skipped="0" time="1.5"><testcase classname="a" name="x"/><testcase classname="a" name="y"/></testsuite>
      <testsuite name="b" tests="1" failures="1" errors="0" skipped="0" time="0.25"><testcase classname="b.C" name="z"><failure message="boom">trace</failure></testcase></testsuite>
    </testsuites>"""
    report = parse_report(two)
    assert (report.total, report.passed, report.failures, report.duration) == (3, 2, 1, 1.75)
    assert report.failed_tests == [FailedTest("b.C::z", "boom")]
    bare = parse_report('<testsuite tests="1" failures="0" errors="0" skipped="0" time="0.1"><testcase classname="m" name="t"/></testsuite>')
    assert (bare.total, bare.passed, bare.failed_tests) == (1, 1, [])


def test_markdown_summary_for_failures():
    assert markdown_summary(parse_report(sample())) == (
        "## ❌ Tests failed\n\n"
        "| Total | Passed | Failed | Errors | Skipped | Duration |\n"
        "|---|---|---|---|---|---|\n"
        "| 5 | 2 | 1 | 1 | 1 | 0.03s |\n\n"
        "### Failures\n\n"
        "- `tests.test_orders::test_discount_rounds_down` — AssertionError: discount must round down\n"
        '- `tests.test_orders::test_saves_order` — failed on setup with "ConnectionError: could not connect to server: Connection refused\n'
    )


def test_markdown_summary_all_green():
    report = Report(total=3, skipped=1, duration=2.0)
    assert markdown_summary(report) == (
        "## ✅ Tests passed\n\n"
        "| Total | Passed | Failed | Errors | Skipped | Duration |\n"
        "|---|---|---|---|---|---|\n"
        "| 3 | 2 | 0 | 0 | 1 | 2.00s |\n"
    )


def test_annotations_escape_workflow_command_syntax():
    assert annotations(parse_report(sample())) == [
        "::error title=tests.test_orders%3A%3Atest_discount_rounds_down::AssertionError: discount must round down",
        '::error title=tests.test_orders%3A%3Atest_saves_order::failed on setup with "ConnectionError: could not connect to server: Connection refused',
    ]
    tricky = Report(total=1, failures=1, failed_tests=[FailedTest("a::b, c", "100% wrong\r\nnext")])
    assert annotations(tricky) == ["::error title=a%3A%3Ab%2C c::100%25 wrong%0D%0Anext"]


def test_cli_prints_summary_to_stdout_and_annotations_to_stderr():
    result = subprocess.run([sys.executable, str(HERE / "junit_summary.py"), str(HERE / "sample-report.xml")], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.startswith("## ❌ Tests failed") and "::error" not in result.stdout
    assert result.stderr.count("::error title=") == 2
    usage = subprocess.run([sys.executable, str(HERE / "junit_summary.py")], capture_output=True, text=True)
    assert usage.returncode == 2 and "usage" in usage.stderr.lower()


# ---------- workflows/ci.yml ----------

@pytest.fixture(scope="module")
def workflow():
    data = yaml.safe_load((HERE / "workflows" / "ci.yml").read_text())
    # YAML 1.1 gotcha: PyYAML reads the key `on` as the boolean True.
    data["on"] = data.pop(True, data.get("on"))
    return data


def all_steps(workflow):
    return [step for job in workflow["jobs"].values() for step in job.get("steps", [])]


def runs(job):
    return "\n".join(step.get("run", "") for step in job.get("steps", []))


def uses(job, prefix):
    return [step for step in job.get("steps", []) if step.get("uses", "").startswith(prefix)]


def test_triggers_permissions_and_concurrency(workflow):
    triggers = workflow["on"]
    assert isinstance(triggers, dict), "use the mapping form of `on:`"
    assert triggers["push"]["branches"] == ["main"], "run on pushes to main (PRs cover other branches)"
    assert "pull_request" in triggers and "pull_request_target" not in triggers
    assert workflow["permissions"] == {"contents": "read"}, "least-privilege GITHUB_TOKEN"
    concurrency = workflow["concurrency"]
    assert "github.ref" in concurrency["group"] and concurrency["cancel-in-progress"] is True


def test_every_job_has_timeout_and_pinned_runner(workflow):
    assert {"lint", "test", "build"} <= set(workflow["jobs"])
    for name, job in workflow["jobs"].items():
        assert 0 < job.get("timeout-minutes", 0) <= 30, f"{name}: set timeout-minutes (≤ 30)"
        assert job["runs-on"].startswith("ubuntu-"), name


def test_actions_are_pinned_to_full_commit_shas(workflow):
    used = [step["uses"] for step in all_steps(workflow) if "uses" in step]
    assert used
    for action in used:
        assert SHA_PIN.match(action), f"pin to a full 40-character commit SHA (with a # vX.Y.Z comment): {action}"
    text = (HERE / "workflows" / "ci.yml").read_text()
    assert all(re.search(re.escape(a) + r"\s+#\s*v\d", text) for a in used), "add a version comment after each SHA"


def test_lint_job(workflow):
    job = workflow["jobs"]["lint"]
    assert uses(job, "actions/checkout@") and uses(job, "astral-sh/setup-uv@")
    commands = runs(job)
    assert "uv sync --locked" in commands
    for tool in ("ruff check", "ruff format --check", "mypy"):
        assert tool in commands, f"lint job should run {tool}"


def test_test_job_uses_postgres_matrix_and_summary(workflow):
    job = workflow["jobs"]["test"]
    postgres = job["services"]["postgres"]
    assert postgres["image"] == "postgres:17-alpine"
    assert "--health-cmd" in postgres["options"] and "pg_isready" in postgres["options"]
    assert any(str(p).startswith("5432:5432") for p in postgres["ports"])
    matrix = job["strategy"]["matrix"]["python-version"]
    assert matrix == ["3.13", "3.14"] and all(isinstance(v, str) for v in matrix), "quote versions so YAML keeps them as strings"
    assert job["strategy"]["fail-fast"] is False
    setup = uses(job, "astral-sh/setup-uv@")
    assert setup and setup[0]["with"]["python-version"] == "${{ matrix.python-version }}"
    assert "localhost:5432" in job["env"]["DATABASE_URL"] and job["env"]["DATABASE_URL"].startswith("postgresql")
    commands = runs(job)
    assert "uv sync --locked" in commands and re.search(r"pytest .*--junitxml[= ]report\.xml", commands)
    summary = [s for s in job["steps"] if "junit_summary.py" in s.get("run", "")]
    assert summary and summary[0].get("if") == "always()", "publish the summary even when tests fail"
    assert "$GITHUB_STEP_SUMMARY" in summary[0]["run"]


def test_build_job_only_on_main_after_checks(workflow):
    job = workflow["jobs"]["build"]
    assert set(job["needs"]) == {"lint", "test"}
    condition = job["if"].replace('"', "'")
    assert "github.event_name == 'push'" in condition and "refs/heads/main" in condition
    build = uses(job, "docker/build-push-action@")
    assert uses(job, "docker/setup-buildx-action@") and build
    assert build[0]["with"]["push"] is False, "no registry credentials yet: build only"
    assert "${{ github.sha }}" in build[0]["with"]["tags"], "tag images with the commit SHA"


def test_no_hardcoded_app_secrets(workflow):
    for name, job in workflow["jobs"].items():
        for step in [job, *job.get("steps", [])]:
            for key, value in (step.get("env") or {}).items():
                if re.search(r"(?i)secret|token|api_key", key):
                    assert "${{ secrets." in str(value), f"{name}: {key} must come from ${{{{ secrets.* }}}} (or not be needed in CI)"


# ---------- workflows/dependabot.yml ----------

def test_dependabot_updates_actions_and_uv():
    config = yaml.safe_load((HERE / "workflows" / "dependabot.yml").read_text())
    assert config["version"] == 2
    ecosystems = {u["package-ecosystem"]: u for u in config["updates"]}
    assert {"github-actions", "uv"} <= set(ecosystems)
    assert all(u["schedule"]["interval"] in ("daily", "weekly", "monthly") for u in ecosystems.values())
