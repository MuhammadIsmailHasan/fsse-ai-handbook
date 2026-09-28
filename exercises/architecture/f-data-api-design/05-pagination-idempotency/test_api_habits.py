from api_habits import cursor_page, create_payment, offset_page


def make_items(ids):
    return [{"id": i} for i in ids]


def test_offset_page():
    items = make_items(range(1, 11))  # ids 1..10
    assert offset_page(items, 0, 3) == make_items([1, 2, 3])
    assert offset_page(items, 3, 3) == make_items([4, 5, 6])
    assert offset_page(items, 9, 3) == make_items([10])  # past the end is fine
    assert offset_page(items, 100, 3) == []


def test_cursor_page_walks_to_the_end():
    items = make_items(range(1, 8))  # ids 1..7
    page, cursor = cursor_page(items, None, 3)
    assert page == make_items([1, 2, 3]) and cursor == 3
    page, cursor = cursor_page(items, cursor, 3)
    assert page == make_items([4, 5, 6]) and cursor == 6
    page, cursor = cursor_page(items, cursor, 3)
    assert page == make_items([7]) and cursor is None  # last page


def test_cursor_is_stable_when_a_row_is_added():
    items = make_items(range(1, 11))
    page1, cursor = cursor_page(items, None, 3)  # [1,2,3]
    # A new row arrives while the user is paging.
    items.append({"id": 11})
    page2, _ = cursor_page(items, cursor, 3)  # still continues after id 3
    assert page2 == make_items([4, 5, 6])  # no duplicates, no skips


def test_offset_can_duplicate_when_a_row_is_inserted_at_front():
    items = make_items(range(1, 11))
    first = offset_page(items, 0, 3)  # [1,2,3]
    items.insert(0, {"id": 0})  # a new row jumps to the front
    second = offset_page(items, 3, 3)  # expected [4,5,6], but shifts
    # id 3 is served twice — the classic offset instability.
    assert {i["id"] for i in first} & {i["id"] for i in second} == {3}


def test_idempotent_payment_charges_once():
    store: dict = {}
    first = create_payment(store, "key-abc", 100000)
    assert first == {"id": "key-abc", "amount": 100000, "charged": True}
    # A retry with the SAME key returns the same result, no second charge.
    again = create_payment(store, "key-abc", 100000)
    assert again == first
    assert len(store) == 1
    # A different action (different key) is a separate charge.
    other = create_payment(store, "key-xyz", 50000)
    assert other["amount"] == 50000
    assert len(store) == 2
