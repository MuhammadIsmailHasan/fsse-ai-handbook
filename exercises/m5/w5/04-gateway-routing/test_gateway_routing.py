"""Checks for gateway_routing.py. Don't edit this file."""

from gateway_routing import pick_backend

ROUTES = [
    ("/orders", "orders-svc"),
    ("/orders/history", "orders-history-svc"),
    ("/products", "catalog-svc"),
    ("/payments", "payments-svc"),
]


def test_simple_match():
    assert pick_backend("/products/42", ROUTES) == "catalog-svc"


def test_longest_prefix_wins():
    assert pick_backend("/orders/history/42", ROUTES) == "orders-history-svc"


def test_shorter_prefix_when_specific_does_not_match():
    assert pick_backend("/orders/42", ROUTES) == "orders-svc"


def test_no_match_returns_none():
    assert pick_backend("/unknown", ROUTES) is None


def test_exact_prefix_match():
    assert pick_backend("/payments", ROUTES) == "payments-svc"


def test_route_order_does_not_matter():
    reordered = list(reversed(ROUTES))
    assert pick_backend("/orders/history/1", reordered) == "orders-history-svc"


def test_empty_routes():
    assert pick_backend("/orders", []) is None
