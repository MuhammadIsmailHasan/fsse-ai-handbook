"""C9 · Your evaluation dataset: evals/cases.jsonl (one JSON object per line). You write this file."""

import json
from pathlib import Path

import pytest

CASES_FILE = Path(__file__).resolve().parents[2] / "evals" / "cases.jsonl"

REQUIRED_TAGS = {"id": 5, "en": 5, "unanswerable": 3, "injection": 3, "critical": 2, "tool": 3, "typo": 2}


@pytest.fixture(scope="module")
def cases():
    if not CASES_FILE.exists():
        pytest.fail(f"Create {CASES_FILE.relative_to(CASES_FILE.parents[1])} — see evals/README.md", pytrace=False)
    rows = []
    for number, line in enumerate(CASES_FILE.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            pytest.fail(f"line {number} is not valid JSON: {error}", pytrace=False)
    return rows


def test_at_least_thirty_cases(cases):
    assert len(cases) >= 30


def test_ids_are_unique_and_non_empty(cases):
    ids = [c.get("id") for c in cases]
    assert all(isinstance(i, str) and i.strip() for i in ids)
    assert len(ids) == len(set(ids))


def test_every_case_has_an_input_and_an_expectation(cases):
    for case in cases:
        assert isinstance(case.get("input"), str) and case["input"].strip(), case.get("id")
        has_expected = bool(str(case.get("expected") or "").strip()) or bool(str(case.get("criteria") or "").strip())
        assert has_expected, f"{case.get('id')}: needs expected or criteria"


def test_tags_are_lists_of_strings(cases):
    for case in cases:
        assert isinstance(case.get("tags"), list) and case["tags"], f"{case.get('id')}: tags must be a non-empty list"
        assert all(isinstance(t, str) for t in case["tags"])


@pytest.mark.parametrize(("tag", "minimum"), sorted(REQUIRED_TAGS.items()))
def test_required_tag_coverage(cases, tag, minimum):
    count = sum(1 for c in cases if tag in c.get("tags", []))
    assert count >= minimum, f"tag '{tag}' has {count} cases, needs at least {minimum}"


def test_unanswerable_cases_are_marked_with_no_relevant_articles(cases):
    for case in cases:
        if "unanswerable" in case["tags"]:
            assert case.get("relevant_ids", None) == [], f"{case['id']}: unanswerable cases need \"relevant_ids\": []"


def test_answerable_rag_cases_name_their_source_articles(cases):
    rag = [c for c in cases if "relevant_ids" in c and c["relevant_ids"]]
    assert len(rag) >= 10
    for case in rag:
        assert all(isinstance(i, str) and i for i in case["relevant_ids"])
