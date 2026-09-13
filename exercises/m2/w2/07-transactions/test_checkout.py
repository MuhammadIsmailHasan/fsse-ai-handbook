"""Tests for place_order. Don't edit this file."""

import threading
from pathlib import Path

import psycopg
import pytest

from checkout import OutOfStock, place_order

HERE = Path(__file__).parent


@pytest.fixture
def shop(db, run_sql):
    run_sql(db, HERE / "shop_schema.sql")
    db.execute(
        "INSERT INTO products (name, price, stock) VALUES ('Notebook', 25000, 10), ('Pen', 5000, 3), ('Mug', 60000, 1)"
    )
    return db


def ids(conn):
    return dict(conn.execute("SELECT name, id FROM products").fetchall())


def stock(conn):
    return dict(conn.execute("SELECT name, stock FROM products").fetchall())


def count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_successful_order(shop):
    p = ids(shop)
    order_id = place_order(shop, user_id=7, items=[(p["Notebook"], 2), (p["Pen"], 3)])

    assert shop.execute("SELECT user_id, total FROM orders WHERE id = %s", (order_id,)).fetchone() == (7, 65000)
    items = shop.execute(
        "SELECT product_id, quantity, unit_price FROM order_items WHERE order_id = %s ORDER BY product_id", (order_id,)
    ).fetchall()
    assert items == sorted([(p["Notebook"], 2, 25000), (p["Pen"], 3, 5000)])
    assert stock(shop) == {"Notebook": 8, "Pen": 0, "Mug": 1}


def test_price_snapshot_is_kept(shop):
    p = ids(shop)
    order_id = place_order(shop, 7, [(p["Notebook"], 1)])
    shop.execute("UPDATE products SET price = 99999 WHERE id = %s", (p["Notebook"],))
    assert shop.execute("SELECT unit_price FROM order_items WHERE order_id = %s", (order_id,)).fetchone()[0] == 25000


def test_insufficient_stock_changes_nothing(shop):
    p = ids(shop)
    with pytest.raises(OutOfStock) as error:
        place_order(shop, 7, [(p["Notebook"], 2), (p["Pen"], 4)])  # Notebook OK, Pen fails
    assert error.value.product_id == p["Pen"]
    assert stock(shop) == {"Notebook": 10, "Pen": 3, "Mug": 1}, "Stock must be unchanged (rollback!)"
    assert count(shop, "orders") == 0 and count(shop, "order_items") == 0


def test_unknown_product_changes_nothing(shop):
    p = ids(shop)
    with pytest.raises(OutOfStock):
        place_order(shop, 7, [(p["Notebook"], 1), (999999, 1)])
    assert stock(shop)["Notebook"] == 10
    assert count(shop, "orders") == 0


@pytest.mark.parametrize("items", [[], [(1, 0)], [(1, -2)]])
def test_invalid_input(shop, items):
    with pytest.raises(ValueError):
        place_order(shop, 7, items)
    assert count(shop, "orders") == 0


def test_last_unit_race_only_one_winner(shop):
    mug = ids(shop)["Mug"]
    schema = shop.execute("SELECT current_schema()").fetchone()[0]
    results = []
    barrier = threading.Barrier(2)

    def customer(user_id):
        conn = psycopg.connect(shop.info.dsn, password="fsse", autocommit=True)
        conn.execute(f"SET search_path TO {schema}")
        try:
            barrier.wait()
            place_order(conn, user_id, [(mug, 1)])
            results.append("ok")
        except OutOfStock:
            results.append("out")
        finally:
            conn.close()

    threads = [threading.Thread(target=customer, args=(user,)) for user in (1, 2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert sorted(results) == ["ok", "out"]
    assert stock(shop)["Mug"] == 0
    assert count(shop, "orders") == 1
