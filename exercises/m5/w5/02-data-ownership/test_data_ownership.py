"""Checks for data_ownership.py. Don't edit this file."""

from data_ownership import Service, find_ownership_violations


def test_clean_boundaries_have_no_violations():
    services = [
        Service("Catalog", owns=("products",), writes=("products",)),
        Service("Orders", owns=("orders",), writes=("orders",)),
    ]
    assert find_ownership_violations(services) == []


def test_writing_another_services_table_is_a_violation():
    services = [
        Service("Catalog", owns=("products",), writes=("products",)),
        Service("Orders", owns=("orders",), writes=("orders", "products")),
    ]
    assert find_ownership_violations(services) == [
        "Orders writes to products owned by Catalog"
    ]


def test_writing_an_unowned_table_is_ignored():
    services = [
        Service("Orders", owns=("orders",), writes=("orders", "scratch_notes")),
    ]
    assert find_ownership_violations(services) == []


def test_multiple_violations_are_sorted():
    services = [
        Service("Catalog", owns=("products",), writes=("products", "orders")),
        Service("Orders", owns=("orders",), writes=("orders", "products")),
    ]
    assert find_ownership_violations(services) == [
        "Catalog writes to orders owned by Orders",
        "Orders writes to products owned by Catalog",
    ]


def test_owning_and_writing_your_own_table_is_fine():
    services = [
        Service("Payments", owns=("payments", "refunds"), writes=("payments", "refunds")),
    ]
    assert find_ownership_violations(services) == []
