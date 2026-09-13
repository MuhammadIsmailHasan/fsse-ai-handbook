"""Reference solution."""

import psycopg


class OutOfStock(Exception):
    def __init__(self, product_id: int):
        super().__init__(f"Product {product_id} is out of stock or doesn't exist")
        self.product_id = product_id


def place_order(conn: psycopg.Connection, user_id: int, items: list[tuple[int, int]]) -> int:
    if not items or any(quantity <= 0 for _, quantity in items):
        raise ValueError("items must be non-empty with positive quantities")

    # Everything inside this block commits together, or rolls back together
    # (an exception leaving the block triggers the rollback).
    with conn.transaction():
        total = 0
        priced_items = []

        # Lock rows in a consistent order (by id) so concurrent orders can't deadlock.
        for product_id, quantity in sorted(items):
            # Conditional UPDATE: the stock check and the decrement are ONE atomic statement,
            # so two customers can't both see "1 left" and both buy it.
            row = conn.execute(
                """UPDATE products
                   SET stock = stock - %s
                   WHERE id = %s AND stock >= %s
                   RETURNING price""",
                (quantity, product_id, quantity),
            ).fetchone()
            if row is None:
                raise OutOfStock(product_id)  # rolls back the decrements already done
            (price,) = row
            total += price * quantity
            priced_items.append((product_id, quantity, price))

        (order_id,) = conn.execute(
            "INSERT INTO orders (user_id, total) VALUES (%s, %s) RETURNING id", (user_id, total)
        ).fetchone()

        with conn.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                [(order_id, product_id, quantity, price) for product_id, quantity, price in priced_items],
            )

    return order_id
