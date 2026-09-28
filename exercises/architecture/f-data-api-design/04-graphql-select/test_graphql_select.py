from graphql_select import count_leaves, graphql_select, over_fetch_count

USER = {
    "id": 1,
    "name": "Ismail",
    "email": "ismail@example.com",
    "avatarUrl": "/a.png",
    "bio": "hello",
    "orders": [
        {"id": 10, "total": 100000, "status": "paid"},
        {"id": 11, "total": 30000, "status": "shipped"},
    ],
}


def test_select_leaf_fields():
    assert graphql_select(USER, {"name": True, "avatarUrl": True}) == {
        "name": "Ismail",
        "avatarUrl": "/a.png",
    }


def test_select_nested_list_fields():
    result = graphql_select(USER, {"name": True, "orders": {"total": True}})
    assert result == {
        "name": "Ismail",
        "orders": [{"total": 100000}, {"total": 30000}],
    }


def test_count_leaves():
    # USER leaves: id, name, email, avatarUrl, bio (5) + 2 orders * 3 fields (6) = 11
    assert count_leaves(USER) == 11
    assert count_leaves({"a": 1}) == 1
    assert count_leaves([]) == 0


def test_over_fetch_count():
    # Mobile card needs only name + each order's total (1 + 2 = 3 leaves).
    selection = {"name": True, "orders": {"total": True}}
    assert over_fetch_count(USER, selection) == 11 - 3
    # Asking for everything wastes nothing extra beyond... itself.
    full_selection = {
        "id": True, "name": True, "email": True, "avatarUrl": True, "bio": True,
        "orders": {"id": True, "total": True, "status": True},
    }
    assert over_fetch_count(USER, full_selection) == 0
