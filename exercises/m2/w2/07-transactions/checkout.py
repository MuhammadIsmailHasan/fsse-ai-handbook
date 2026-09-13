"""M2 · W2 · 07 — All-or-nothing checkout with a database transaction."""

import psycopg


class OutOfStock(Exception):
    """Raised when a product is missing or doesn't have enough stock."""

    def __init__(self, product_id: int):
        super().__init__(f"Product {product_id} is out of stock or doesn't exist")
        self.product_id = product_id


def place_order(conn: psycopg.Connection, user_id: int, items: list[tuple[int, int]]) -> int:
    # YOUR CODE HERE
    raise NotImplementedError
