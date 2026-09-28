"""Architecture · F — Build a tiny index and count the work.

Rows look like: {"id": int, "user_id": int, "status": str}

- linear_search scans EVERY row (and reports how many it touched).
- An equality index (dict: value -> rows) answers the same query while
  touching far fewer rows.
- A composite (user_id, status) index can serve a query on user_id alone,
  but NOT on status alone — like a phone book sorted by (last, first).
"""


def linear_search(rows: list[dict], field: str, value) -> tuple[list[dict], int]:
    """Return (matching_rows, rows_scanned). rows_scanned is always len(rows)."""
    # YOUR CODE HERE
    return [], -1


def build_index(rows: list[dict], field: str) -> dict:
    """Return {value: [rows with that value]} for a single column."""
    # YOUR CODE HERE
    return {}


def indexed_search(index: dict, value) -> list[dict]:
    """Look up rows for a value in O(1); return [] if the value is absent."""
    # YOUR CODE HERE
    return []


def build_composite_index(rows: list[dict], field_a: str, field_b: str) -> dict:
    """Return {(a_value, b_value): [rows]} — a composite index over two columns."""
    # YOUR CODE HERE
    return {}


def search_composite_by_first(index: dict, a_value) -> list[dict]:
    """Serve a query on the FIRST column alone by scanning the composite keys.

    Return all rows whose key's first element == a_value, preserving row order.
    """
    # YOUR CODE HERE
    return []
