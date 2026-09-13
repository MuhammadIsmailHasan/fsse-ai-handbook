"""Automatic checks. Don't edit this file — make these pass by editing form_data.py."""

import pytest

from form_data import describe_user, parse_age, parse_height_m, parse_newsletter


@pytest.mark.parametrize(("text", "expected"), [("25", 25), (" 25 ", 25), ("\t40\n", 40)])
def test_parse_age(text, expected):
    result = parse_age(text)
    assert result == expected
    assert isinstance(result, int)


@pytest.mark.parametrize(("text", "expected"), [("172", 1.72), (" 180 ", 1.8), ("165.5", 1.655)])
def test_parse_height_m(text, expected):
    assert parse_height_m(text) == pytest.approx(expected)


@pytest.mark.parametrize("text", ["yes", "Y", " TRUE ", "Yes"])
def test_parse_newsletter_true(text):
    assert parse_newsletter(text) is True


@pytest.mark.parametrize("text", ["no", "", "false", "0", "yess", "maybe"])
def test_parse_newsletter_false(text):
    assert parse_newsletter(text) is False


def test_describe_user():
    assert describe_user("Ana", 20) == "Ana (20 years old)"
    assert describe_user("Budi Santoso", 31) == "Budi Santoso (31 years old)"
