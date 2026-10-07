"""C3 · Matching — the pure logic, with no HTTP: find skills, compare a CV with a job."""

import pytest

from careerpilot_ai.matching import NoSkillsFound, compare, extract_skills


def test_finds_known_skills_case_insensitively():
    assert extract_skills("Python, FLASK and Docker") == {"python", "flask", "docker"}


def test_whole_words_only():
    assert extract_skills("PostgreSQL and NoSQL") == {"postgresql"}
    assert extract_skills("I use GitHub") == set()
    assert extract_skills("Pythonic code") == set()


def test_punctuation_and_hyphens_do_not_hide_a_skill():
    assert extract_skills("(python)") == {"python"}
    assert extract_skills("python-based services") == {"python"}


def test_multi_word_skill_matches_as_a_phrase():
    assert extract_skills("git and GitHub Actions") == {"git", "github actions"}
    assert extract_skills("github and actions") == set()


def test_no_skills_gives_empty_set():
    assert extract_skills("I like long walks") == set()


def test_compare_returns_score_level_matched_and_missing():
    from p3_support import CV, JOB

    result = compare(CV, JOB)
    assert result == {
        "score": 57,
        "level": "partial",
        "matched_skills": ["docker", "git", "postgresql", "python"],
        "missing_skills": ["aws", "fastapi", "sql"],
    }


def test_full_overlap_is_100_strong():
    result = compare("python flask", "python flask")
    assert result["score"] == 100
    assert result["level"] == "strong"
    assert result["missing_skills"] == []


def test_three_of_four_is_75_strong():
    result = compare("python flask sql", "python flask sql docker")
    assert result["score"] == 75
    assert result["level"] == "strong"


def test_two_of_three_is_67_partial():
    result = compare("python docker", "python docker aws")
    assert result["score"] == 67
    assert result["level"] == "partial"


def test_one_of_three_is_33_weak():
    result = compare("python", "python docker aws")
    assert result["score"] == 33
    assert result["level"] == "weak"


def test_no_overlap_is_0_weak():
    result = compare("react", "python docker")
    assert result["score"] == 0
    assert result["level"] == "weak"
    assert result["matched_skills"] == []


def test_extra_cv_skills_do_not_raise_the_score():
    assert compare("python docker aws react redis", "python docker")["score"] == 100


def test_job_without_skills_raises():
    with pytest.raises(NoSkillsFound):
        compare("python", "we are a friendly team")


def test_no_skills_found_is_a_value_error():
    assert issubclass(NoSkillsFound, ValueError)
