from stores import (
    join_orders,
    order_total,
    rename_user_document,
    rename_user_relational,
)


def relational_data():
    users = {7: {"name": "Ismail"}, 9: {"name": "Sari"}}
    orders = [
        {"id": 1, "user_id": 7, "items": [{"qty": 2, "price": 50000}]},
        {"id": 2, "user_id": 7, "items": [{"qty": 1, "price": 30000}]},
        {"id": 3, "user_id": 9, "items": [{"qty": 3, "price": 10000}]},
    ]
    return users, orders


def document_data():
    return [
        {"id": 1, "user_id": 7, "user_name": "Ismail", "items": [{"qty": 2, "price": 50000}]},
        {"id": 2, "user_id": 7, "user_name": "Ismail", "items": [{"qty": 1, "price": 30000}]},
        {"id": 3, "user_id": 9, "user_name": "Sari", "items": [{"qty": 3, "price": 10000}]},
    ]


def test_order_total():
    assert order_total({"items": [{"qty": 2, "price": 50000}, {"qty": 1, "price": 30000}]}) == 130000
    assert order_total({"items": []}) == 0


def test_join_orders():
    users, orders = relational_data()
    result = join_orders(orders, users)
    assert result == [
        {"order_id": 1, "user_name": "Ismail", "total": 100000},
        {"order_id": 2, "user_name": "Ismail", "total": 30000},
        {"order_id": 3, "user_name": "Sari", "total": 30000},
    ]


def test_relational_rename_is_one_write():
    users, orders = relational_data()
    writes = rename_user_relational(users, 7, "Muhammad")
    assert writes == 1
    # The join now shows the new name everywhere, from a single source of truth.
    result = join_orders(orders, users)
    assert [r["user_name"] for r in result] == ["Muhammad", "Muhammad", "Sari"]


def test_document_rename_touches_every_copy():
    orders = document_data()
    changed = rename_user_document(orders, 7, "Muhammad")
    # User 7 appears in two orders, so two documents must be rewritten.
    assert changed == 2
    assert [o["user_name"] for o in orders] == ["Muhammad", "Muhammad", "Sari"]
