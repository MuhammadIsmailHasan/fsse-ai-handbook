import time

from queens import count_queen_placements, first_queen_board

KNOWN_COUNTS = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}


def test_known_counts():
    for n, expected in KNOWN_COUNTS.items():
        assert count_queen_placements(n) == expected, f"n={n}"


def test_no_board_and_negative_sizes():
    assert count_queen_placements(0) == 0
    assert count_queen_placements(-3) == 0


def test_first_board_for_four():
    assert first_queen_board(4) == [".Q..", "...Q", "Q...", "..Q."]


def test_first_board_for_one():
    assert first_queen_board(1) == ["Q"]


def test_no_board_exists():
    assert first_queen_board(2) is None
    assert first_queen_board(3) is None


def test_first_board_is_really_valid():
    for n in (5, 6, 7, 8):
        board = first_queen_board(n)
        assert board is not None and len(board) == n
        assert all(len(row) == n and row.count("Q") == 1 for row in board)
        cols = [row.index("Q") for row in board]
        assert len(set(cols)) == n                                  # no shared column
        assert len({r + c for r, c in enumerate(cols)}) == n        # no shared rising diagonal
        assert len({r - c for r, c in enumerate(cols)}) == n        # no shared falling diagonal


def test_counting_is_fast_enough_for_nine():
    # Scanning the whole board for each candidate is too slow here; sets make it instant.
    started = time.perf_counter()
    assert count_queen_placements(9) == 352
    assert time.perf_counter() - started < 2.0
