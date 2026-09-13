"""Turn a pytest JUnit XML report into a GitHub job summary and error annotations. See README.md.

In CI:  uv run python junit_summary.py report.xml >> "$GITHUB_STEP_SUMMARY"
"""

import sys
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
        raise NotImplementedError


def parse_report(xml_text: str) -> Report:
    raise NotImplementedError


def markdown_summary(report: Report) -> str:
    raise NotImplementedError


def annotations(report: Report) -> list[str]:
    raise NotImplementedError


def main(argv: list[str]) -> int:
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main(sys.argv))
