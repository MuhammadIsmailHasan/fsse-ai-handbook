import copy
import random
import time

import pytest

from sorting_basics import kth_largest, merge_intervals, rank_jobs

JOBS = [
    {"title": "Data Analyst", "salary_max": 12_000_000, "posted_on": "2026-09-01"},
    {"title": "Backend Engineer", "salary_max": 18_000_000, "posted_on": "2026-08-20"},
    {"title": "QA Engineer", "salary_max": None, "posted_on": "2026-09-10"},
    {"title": "AI Engineer", "salary_max": 18_000_000, "posted_on": "2026-09-05"},
    {"title": "Android Dev", "salary_max": 12_000_000, "posted_on": "2026-09-01"},
    {"title": "Admin", "salary_max": None, "posted_on": "2026-09-11"},
]


def test_rank_jobs():
    before = copy.deepcopy(JOBS)
    assert [j["title"] for j in rank_jobs(JOBS)] == ["AI Engineer", "Backend Engineer", "Android Dev", "Data Analyst", "Admin", "QA Engineer"]
    assert JOBS == before, "return a new list"


def test_rank_jobs_random():
    rng = random.Random(71)
    for _ in range(200):
        jobs = [{"title": rng.choice("ABCD"), "salary_max": rng.choice([None, 5, 10]), "posted_on": f"2026-09-0{rng.randint(1, 3)}"} for _ in range(rng.randint(0, 10))]
        expected = sorted(jobs, key=lambda j: (j["salary_max"] is None, -(j["salary_max"] or 0), [-ord(c) for c in j["posted_on"]], j["title"]))
        assert rank_jobs(jobs) == expected


@pytest.mark.parametrize(
    ("intervals", "expected"),
    [([[8, 10], [1, 3], [2, 6], [15, 18]], [[1, 6], [8, 10], [15, 18]]), ([[1, 3], [3, 5]], [[1, 5]]), ([], []), ([[1, 10], [2, 3]], [[1, 10]]), ([[5, 5]], [[5, 5]])],
)
def test_merge_intervals(intervals, expected):
    assert merge_intervals(intervals) == expected


def test_merge_intervals_random():
    rng = random.Random(72)
    for _ in range(300):
        intervals = []
        for _ in range(rng.randint(0, 8)):
            a = rng.randint(0, 20)
            intervals.append([a, a + rng.randint(0, 5)])
        covered = sorted({x for a, b in intervals for x in range(a, b + 1)})
        merged = merge_intervals(intervals)
        assert sorted({x for a, b in merged for x in range(a, b + 1)}) == covered
        assert all(merged[i][1] < merged[i + 1][0] for i in range(len(merged) - 1))


def test_kth_largest():
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
    rng = random.Random(73)
    for _ in range(300):
        nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(nums))
        assert kth_largest(nums, k) == sorted(nums, reverse=True)[k - 1]


def test_kth_largest_small_k_is_fast():
    nums = list(range(1_000_000))
    random.Random(74).shuffle(nums)
    started = time.perf_counter()
    assert kth_largest(nums, 3) == 999_997
    assert time.perf_counter() - started < 1.5
