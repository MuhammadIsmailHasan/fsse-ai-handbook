"""Architecture · F — Model the same data two ways (solution)."""


def order_total(order: dict) -> int:
    return sum(item["qty"] * item["price"] for item in order["items"])


# --- Relational model -------------------------------------------------------


def join_orders(orders: list[dict], users: dict[int, dict]) -> list[dict]:
    return [
        {
            "order_id": order["id"],
            "user_name": users[order["user_id"]]["name"],
            "total": order_total(order),
        }
        for order in orders
    ]


def rename_user_relational(users: dict[int, dict], user_id: int, new_name: str) -> int:
    users[user_id]["name"] = new_name
    return 1


# --- Document model ---------------------------------------------------------


def rename_user_document(orders: list[dict], user_id: int, new_name: str) -> int:
    changed = 0
    for order in orders:
        if order["user_id"] == user_id:
            order["user_name"] = new_name
            changed += 1
    return changed
