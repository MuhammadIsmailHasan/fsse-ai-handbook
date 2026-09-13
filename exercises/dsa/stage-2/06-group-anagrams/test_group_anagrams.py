import random
import time

import pytest

from group_anagrams import group_anagrams


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (["eat", "tea", "tan", "ate", "nat", "bat"], [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]),
        ([], []),
        ([""], [[""]]),
        (["a", "a", "b"], [["a", "a"], ["b"]]),
        (["ab", "ba", "abc", "cab", "b"], [["ab", "ba"], ["abc", "cab"], ["b"]]),
    ],
)
def test_examples(words, expected):
    assert group_anagrams(words) == expected


def brute(words):
    groups = []
    for word in words:
        for group in groups:
            if sorted(group[0]) == sorted(word):
                group.append(word)
                break
        else:
            groups.append([word])
    return groups


def test_matches_brute_force():
    rng = random.Random(21)
    for _ in range(200):
        words = ["".join(rng.choice("abc") for _ in range(rng.randint(0, 3))) for _ in range(rng.randint(0, 12))]
        assert group_anagrams(words) == brute(words)


def test_scales_linearly_in_number_of_words():
    rng = random.Random(1)
    words = ["".join(rng.choice("abcdefghij") for _ in range(8)) for _ in range(60_000)]
    started = time.perf_counter()
    groups = group_anagrams(words)
    assert sum(map(len, groups)) == 60_000
    assert time.perf_counter() - started < 1.5, "compare each word with every group is O(n²) — use a dict key"
