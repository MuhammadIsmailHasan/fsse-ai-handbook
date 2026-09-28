"""Architecture · F — Model the same data two ways.

Two tiny in-memory "stores" for the same orders:

- Relational: users and orders are separate; an order references a user by id.
- Document:   each order embeds a COPY of the user's name.

The tests show the trade-off: renaming a user is one write in the relational
model, but one write PER order in the document model.
"""


def order_total(order: dict) -> int:
    """Sum qty * price over an order's items."""
    # YOUR CODE HERE
    return -1


# --- Relational model -------------------------------------------------------
# users:  {user_id: {"name": str}}
# orders: [{"id": int, "user_id": int, "items": [{"qty": int, "price": int}]}]


def join_orders(orders: list[dict], users: dict[int, dict]) -> list[dict]:
    """Return [{"order_id", "user_name", "total"}] by looking up each user by id."""
    # YOUR CODE HERE
    return []


def rename_user_relational(users: dict[int, dict], user_id: int, new_name: str) -> int:
    """Rename a user in ONE place. Return the number of records written (1)."""
    # YOUR CODE HERE
    return -1


# --- Document model ---------------------------------------------------------
# orders: [{"id": int, "user_id": int, "user_name": str, "items": [...]}]


def rename_user_document(orders: list[dict], user_id: int, new_name: str) -> int:
    """Rename a user everywhere the name was copied. Return how many orders changed."""
    # YOUR CODE HERE
    return -1
