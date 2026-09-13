"""Turn a pytest JUnit XML report into a GitHub job summary and error annotations.

In CI:  uv run python junit_summary.py report.xml >> "$GITHUB_STEP_SUMMARY"
"""

import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FailedTest:
    test_id: str  # "tests.test_orders::test_discount_rounds_down"
    message: str  # first line of the failure/error message


@dataclass
class Report:
    total: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    duration: float = 0.0
    failed_tests: list[FailedTest] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return self.total - self.failures - self.errors - self.skipped


def parse_report(xml_text: str) -> Report:
    root = ET.fromstring(xml_text)
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    report = Report()
    for suite in suites:
        report.total += int(suite.get("tests", 0))
        report.failures += int(suite.get("failures", 0))
        report.errors += int(suite.get("errors", 0))
        report.skipped += int(suite.get("skipped", 0))
        report.duration += float(suite.get("time", 0))
        for case in suite.iter("testcase"):
            problem = case.find("failure")
            if problem is None:
                problem = case.find("error")
            if problem is not None:
                message = (problem.get("message") or "").splitlines()
                test_id = f"{case.get('classname')}::{case.get('name')}"
                report.failed_tests.append(FailedTest(test_id, message[0] if message else ""))
    return report


def markdown_summary(report: Report) -> str:
    ok = report.failures == 0 and report.errors == 0
    lines = [
        "## ✅ Tests passed" if ok else "## ❌ Tests failed",
        "",
        "| Total | Passed | Failed | Errors | Skipped | Duration |",
        "|---|---|---|---|---|---|",
        f"| {report.total} | {report.passed} | {report.failures} | {report.errors} | {report.skipped} | {report.duration:.2f}s |",
    ]
    if report.failed_tests:
        lines += ["", "### Failures", ""]
        lines += [f"- `{t.test_id}` — {t.message}" for t in report.failed_tests]
    return "\n".join(lines) + "\n"


def _escape_data(value: str) -> str:
    # GitHub workflow commands: the message part escapes %, CR and LF…
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(value: str) -> str:
    # …and properties (title=…) also escape ":" and ",", which would otherwise end the property.
    return _escape_data(value).replace(":", "%3A").replace(",", "%2C")


def annotations(report: Report) -> list[str]:
    return [f"::error title={_escape_property(t.test_id)}::{_escape_data(t.message)}" for t in report.failed_tests]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: junit_summary.py REPORT.xml", file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as file:
        report = parse_report(file.read())
    print(markdown_summary(report))
    for line in annotations(report):
        print(line, file=sys.stderr)  # stderr: shows as annotations in the log, not in the summary file
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
