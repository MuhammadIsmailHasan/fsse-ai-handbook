from index_lookup import (
    build_composite_index,
    build_index,
    indexed_search,
    linear_search,
    search_composite_by_first,
)

ROWS = [
    {"id": 1, "user_id": 7, "status": "paid"},
    {"id": 2, "user_id": 7, "status": "shipped"},
    {"id": 3, "user_id": 9, "status": "paid"},
    {"id": 4, "user_id": 7, "status": "paid"},
    {"id": 5, "user_id": 9, "status": "shipped"},
]


def ids(rows):
    return sorted(row["id"] for row in rows)


def test_linear_search_scans_everything():
    matches, scanned = linear_search(ROWS, "user_id", 7)
    assert ids(matches) == [1, 2, 4]
    assert scanned == len(ROWS)  # always reads every row


def test_indexed_search_touches_fewer_rows():
    index = build_index(ROWS, "user_id")
    assert ids(indexed_search(index, 7)) == [1, 2, 4]
    assert ids(indexed_search(index, 9)) == [3, 5]
    assert indexed_search(index, 999) == []  # absent value


def test_composite_serves_first_column():
    index = build_composite_index(ROWS, "user_id", "status")
    # Exact (user_id, status) lookup:
    assert ids(index[(7, "paid")]) == [1, 4]
    # First column alone (user_id) is served by scanning the composite keys:
    assert ids(search_composite_by_first(index, 7)) == [1, 2, 4]
    assert ids(search_composite_by_first(index, 9)) == [3, 5]


def test_composite_cannot_index_second_column_alone():
    # There is no key by status alone; you would have to scan every key/row.
    index = build_composite_index(ROWS, "user_id", "status")
    assert ("paid",) not in index
    assert "paid" not in index
