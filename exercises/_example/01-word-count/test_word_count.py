"""Automatic checks for the word count exercise. Don't edit this file."""

from word_count import count_words


def test_empty_text_returns_empty_dict():
    assert count_words("") == {}


def test_counts_repeated_words():
    assert count_words("to be or not to be") == {"to": 2, "be": 2, "or": 1, "not": 1}


def test_ignores_case():
    assert count_words("Hi hi HI") == {"hi": 3}


def test_handles_extra_whitespace():
    assert count_words("  one   two\none\t") == {"one": 2, "two": 1}
