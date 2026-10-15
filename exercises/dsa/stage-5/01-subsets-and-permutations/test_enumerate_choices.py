import itertools

from enumerate_choices import (
    permutations,
    permutations_no_duplicates,
    subsets,
    subsets_no_duplicates,
)


def normalize(lists):
    """Compare results without caring about the order the lists came back in."""
    return sorted(tuple(item) for item in lists)


def reference_subsets(nums):
    out = []
    for size in range(len(nums) + 1):
        out.extend(itertools.combinations(nums, size))
    return out


def test_subsets_of_two():
    assert normalize(subsets([1, 2])) == [(), (1,), (1, 2), (2,)]


def test_subsets_keeps_the_input_order_inside_each_subset():
    assert [3, 1] in subsets([3, 1])
    assert [1, 3] not in subsets([3, 1])


def test_subsets_count_is_two_to_the_n():
    assert len(subsets([1, 2, 3, 4, 5])) == 32
    assert normalize(subsets([1, 2, 3, 4, 5])) == normalize(reference_subsets([1, 2, 3, 4, 5]))


def test_subsets_of_empty_and_single():
    assert subsets([]) == [[]]
    assert normalize(subsets([7])) == [(), (7,)]


def test_subsets_returns_copies_not_one_shared_list():
    result = subsets([1, 2])
    assert len({id(item) for item in result}) == len(result)
    assert normalize(result) == [(), (1,), (1, 2), (2,)]


def test_subsets_no_duplicates():
    assert normalize(subsets_no_duplicates([1, 2, 2])) == [
        (),
        (1,),
        (1, 2),
        (1, 2, 2),
        (2,),
        (2, 2),
    ]


def test_subsets_no_duplicates_all_equal():
    assert normalize(subsets_no_duplicates([4, 4, 4])) == [(), (4,), (4, 4), (4, 4, 4)]


def test_subsets_no_duplicates_matches_a_slow_reference():
    nums = [2, 1, 2, 3, 1]
    expected = sorted({tuple(sorted(combo)) for combo in reference_subsets(nums)})
    assert normalize(subsets_no_duplicates(nums)) == expected


def test_permutations_of_three():
    assert normalize(permutations([1, 2, 3])) == normalize(itertools.permutations([1, 2, 3]))


def test_permutations_count_is_n_factorial():
    assert len(permutations([1, 2, 3, 4])) == 24
    assert all(sorted(order) == [1, 2, 3, 4] for order in permutations([1, 2, 3, 4]))


def test_permutations_of_empty_and_single():
    assert permutations([]) == [[]]
    assert permutations([9]) == [[9]]


def test_permutations_no_duplicates():
    assert normalize(permutations_no_duplicates([1, 1, 2])) == [(1, 1, 2), (1, 2, 1), (2, 1, 1)]


def test_permutations_no_duplicates_matches_a_slow_reference():
    nums = [3, 3, 1, 1]
    expected = sorted(set(itertools.permutations(nums)))
    assert normalize(permutations_no_duplicates(nums)) == expected


def test_permutations_no_duplicates_all_equal():
    assert permutations_no_duplicates([5, 5, 5]) == [[5, 5, 5]]
