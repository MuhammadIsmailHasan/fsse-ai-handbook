"""Automatic checks. Don't edit — make them pass by editing slots.py."""

import pytest

from slots import free_slots, merge_ranges, to_minutes, to_text


@pytest.mark.parametrize(("text", "minutes"), [("00:00", 0), ("09:30", 570), ("17:00", 1020), ("23:59", 1439)])
def test_time_conversion_both_ways(text, minutes):
    assert to_minutes(text) == minutes
    assert to_text(minutes) == text


def test_merge_ranges():
    assert merge_ranges([(600, 720), (540, 660)]) == [(540, 720)]
    assert merge_ranges([(600, 660), (540, 570)]) == [(540, 570), (600, 660)]
    assert merge_ranges([(600, 660), (660, 700)]) == [(600, 700)]  # touching ranges merge
    assert merge_ranges([(500, 900), (600, 700)]) == [(500, 900)]  # contained range
    assert merge_ranges([]) == []


def test_example_from_readme():
    busy = [("13:00", "14:00"), ("09:00", "10:30")]
    assert free_slots(busy, 60) == [("10:30", "13:00"), ("14:00", "17:00")]


def test_no_busy_ranges_means_whole_day():
    assert free_slots([], 30) == [("09:00", "17:00")]


def test_fully_busy_day():
    assert free_slots([("08:00", "18:00")], 15) == []


def test_overlapping_and_outside_day_ranges():
    busy = [("08:00", "09:45"), ("09:30", "11:00"), ("16:30", "19:00")]
    assert free_slots(busy, 60) == [("11:00", "16:30")]


def test_gap_exactly_long_enough_is_included():
    busy = [("09:00", "12:00"), ("12:45", "17:00")]
    assert free_slots(busy, 45) == [("12:00", "12:45")]
    assert free_slots(busy, 46) == []


def test_custom_day_window():
    assert free_slots([("10:00", "11:00")], 30, day_start="08:00", day_end="12:00") == [
        ("08:00", "10:00"),
        ("11:00", "12:00"),
    ]
