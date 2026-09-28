"""Architecture · F — Pagination and idempotency keys.

- offset_page: classic "skip N, take M".
- cursor_page: "give me the next M after this id" — stable when rows are inserted.
- create_payment: charges ONCE even if called again with the same idempotency key.

Items are dicts with an "id" key, kept in ascending id order.
"""


def offset_page(items: list[dict], offset: int, limit: int) -> list[dict]:
    """Return the slice starting at `offset`, at most `limit` items."""
    # YOUR CODE HERE
    return []


def cursor_page(items: list[dict], after_id, limit: int) -> tuple[list[dict], object]:
    """Return (page, next_cursor).

    - after_id is None → start from the beginning.
    - after_id set → start right after the item whose id == after_id.
    - next_cursor is the id of the last returned item, or None if this is the last page.
    """
    # YOUR CODE HERE
    return [], None


def create_payment(store: dict, key: str, amount: int) -> dict:
    """Idempotent create. If `key` was seen, return the stored result unchanged.
    Otherwise create {"id": <key>, "amount": amount, "charged": True}, store, return it."""
    # YOUR CODE HERE
    return {}
