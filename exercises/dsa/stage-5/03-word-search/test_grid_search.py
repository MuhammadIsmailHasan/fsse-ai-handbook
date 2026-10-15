import copy

from grid_search import count_routes, exists, find_words

BOARD = [
    ["C", "A", "T"],
    ["X", "R", "E"],
    ["Y", "Z", "D"],
]


def test_word_found_along_a_bending_path():
    assert exists(copy.deepcopy(BOARD), "CARED") is True


def test_word_not_found_because_steps_are_not_diagonal():
    assert exists(copy.deepcopy(BOARD), "CRY") is False


def test_straight_words():
    assert exists(copy.deepcopy(BOARD), "CAT") is True
    assert exists(copy.deepcopy(BOARD), "CXY") is True
    assert exists(copy.deepcopy(BOARD), "TED") is True


def test_a_cell_cannot_be_reused():
    board = [["A", "B"], ["C", "D"]]
    assert exists(board, "ABA") is False


def test_empty_word_and_missing_letters():
    assert exists(copy.deepcopy(BOARD), "") is True
    assert exists(copy.deepcopy(BOARD), "Q") is False
    assert exists([], "A") is False
    assert exists([[]], "A") is False


def test_board_is_left_unchanged():
    board = copy.deepcopy(BOARD)
    exists(board, "CARED")
    exists(board, "NOPE")
    assert board == BOARD


def test_repeated_letters_need_real_backtracking():
    board = [
        ["A", "A", "A"],
        ["A", "A", "A"],
        ["A", "A", "B"],
    ]
    assert exists(copy.deepcopy(board), "AAAAAAAAB") is True
    assert exists(copy.deepcopy(board), "AAAAAAAAAB") is False


def test_find_words_is_sorted_and_deduplicated():
    assert find_words(copy.deepcopy(BOARD), ["CAT", "TED", "CAT", "DOG", "CARED"]) == [
        "CARED",
        "CAT",
        "TED",
    ]
    assert find_words(copy.deepcopy(BOARD), ["DOG"]) == []


def test_count_routes_small():
    assert count_routes([["S", "."], ["E", "."]]) == 1


def test_count_routes_with_a_blocked_cell():
    grid = [
        ["S", ".", ".", "."],
        [".", ".", ".", "."],
        [".", ".", "E", "#"],
    ]
    assert count_routes(grid) == 2


def test_count_routes_corner_to_corner():
    grid = [
        ["S", ".", ".", "."],
        [".", ".", ".", "."],
        [".", ".", ".", "E"],
    ]
    assert count_routes(grid) == 4


def test_count_routes_impossible():
    assert count_routes([[".", "#"], ["E", "S"]]) == 0      # E is reached too early
    assert count_routes([["S", "."], ["E", "#"]]) == 0      # one open cell is left over


def test_count_routes_leaves_the_grid_unchanged():
    grid = [["S", "."], ["E", "."]]
    before = copy.deepcopy(grid)
    count_routes(grid)
    assert grid == before
