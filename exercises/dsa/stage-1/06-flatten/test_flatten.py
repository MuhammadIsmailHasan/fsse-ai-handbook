import copy

from flatten import flatten, max_depth


def test_flatten_any_depth():
    assert flatten([1, [2, [3, 4]], [], 5]) == [1, 2, 3, 4, 5]
    assert flatten([[[["deep"]]]]) == ["deep"]
    assert flatten([]) == []
    assert flatten(["ab", ["cd"]]) == ["ab", "cd"]  # strings are not split


def test_flatten_does_not_modify_input():
    data = [1, [2, [3]]]
    before = copy.deepcopy(data)
    flatten(data)
    assert data == before


def test_max_depth():
    assert max_depth([]) == 1
    assert max_depth([1, 2]) == 1
    assert max_depth([1, [2, [3]]]) == 3
    assert max_depth([[], [[]], [1]]) == 3
