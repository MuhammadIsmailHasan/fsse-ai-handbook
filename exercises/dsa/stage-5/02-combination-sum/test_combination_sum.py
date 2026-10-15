import time

from combination_sum import can_split_into_equal_groups, combination_sum, combination_sum_once


def normalize(lists):
    return sorted(tuple(item) for item in lists)


def test_combination_sum_example():
    assert normalize(combination_sum([2, 3, 5], 8)) == [(2, 2, 2, 2), (2, 3, 3), (3, 5)]


def test_combination_sum_reuses_a_candidate():
    assert normalize(combination_sum([3], 9)) == [(3, 3, 3)]


def test_combination_sum_no_solution():
    assert combination_sum([4, 6], 7) == []


def test_combination_sum_target_zero_gives_the_empty_combination():
    assert combination_sum([2, 3], 0) == [[]]


def test_combination_sum_every_combination_is_sorted_and_unique():
    result = combination_sum([2, 3, 6, 7], 7)
    assert all(list(combo) == sorted(combo) for combo in result)
    assert len(result) == len({tuple(combo) for combo in result})
    assert normalize(result) == [(2, 2, 3), (7,)]


def test_combination_sum_once_example():
    assert normalize(combination_sum_once([10, 1, 2, 7, 6, 1, 5], 8)) == [
        (1, 1, 6),
        (1, 2, 5),
        (1, 7),
        (2, 6),
    ]


def test_combination_sum_once_uses_each_element_at_most_once():
    assert normalize(combination_sum_once([2, 5, 2, 1, 2], 5)) == [(1, 2, 2), (5,)]


def test_combination_sum_once_cannot_reuse_a_single_element():
    assert combination_sum_once([4], 8) == []


def test_combination_sum_once_all_equal_values():
    assert normalize(combination_sum_once([3, 3, 3], 6)) == [(3, 3)]


def test_split_into_equal_groups_true():
    assert can_split_into_equal_groups([4, 3, 2, 3, 5, 2, 1], 4) is True


def test_split_into_equal_groups_total_does_not_divide():
    assert can_split_into_equal_groups([1, 2, 3, 4], 3) is False


def test_split_into_equal_groups_one_number_too_big():
    assert can_split_into_equal_groups([2, 2, 2, 10], 4) is False


def test_split_into_equal_groups_edge_cases():
    assert can_split_into_equal_groups([5], 1) is True
    assert can_split_into_equal_groups([1, 2], 3) is False     # fewer numbers than groups
    assert can_split_into_equal_groups([2, 2, 2, 2], 4) is True
    assert can_split_into_equal_groups([3, 3, 3, 3], 2) is True


def test_split_into_equal_groups_needs_pruning_to_be_fast():
    # Without pruning this search explodes. With it, the answer is immediate.
    nums = [2, 2, 2, 2, 3, 4, 5, 5, 5, 6, 6, 6, 7, 8, 8, 9]
    started = time.perf_counter()
    assert can_split_into_equal_groups(nums, 4) is True
    assert can_split_into_equal_groups([*nums, 1], 4) is False
    assert time.perf_counter() - started < 2.0
