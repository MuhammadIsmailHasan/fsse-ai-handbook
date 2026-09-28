"""Architecture · F — Pagination and idempotency keys (solution)."""


def offset_page(items: list[dict], offset: int, limit: int) -> list[dict]:
    return items[offset : offset + limit]


def cursor_page(items: list[dict], after_id, limit: int) -> tuple[list[dict], object]:
    start = 0
    if after_id is not None:
        for i, item in enumerate(items):
            if item["id"] == after_id:
                start = i + 1
                break
    page = items[start : start + limit]
    next_cursor = page[-1]["id"] if start + limit < len(items) and page else None
    return page, next_cursor


def create_payment(store: dict, key: str, amount: int) -> dict:
    if key in store:
        return store[key]
    result = {"id": key, "amount": amount, "charged": True}
    store[key] = result
    return result
