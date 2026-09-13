"""Automatic checks. Don't edit — fix buggy_report.py until they pass."""

import pytest

from buggy_report import average_sale_value, best_seller, revenue_for_category, summary_line, total_revenue

SALES = [
    ("tea", "Drinks", 3, 15_000),
    ("croissant", "Bakery", 2, 25_000),
    ("coffee", "Drinks", 1, 30_000),
]


def test_total_revenue_counts_every_sale():
    assert total_revenue(SALES) == 125_000
    assert total_revenue([("tea", "Drinks", 1, 15_000)]) == 15_000


def test_average_sale_value():
    assert average_sale_value(SALES) == pytest.approx(125_000 / 3)


def test_average_sale_value_with_no_sales():
    assert average_sale_value([]) == 0.0


def test_revenue_for_category_ignores_case():
    assert revenue_for_category(SALES, "drinks") == 75_000
    assert revenue_for_category(SALES, "BAKERY") == 50_000
    assert revenue_for_category(SALES, "Toys") == 0


def test_best_seller():
    assert best_seller(SALES) == "tea"
    assert best_seller([]) is None


def test_summary_line():
    assert summary_line(SALES) == "3 sales · revenue Rp 125000 · best seller: Tea"


def test_summary_line_with_no_sales():
    assert summary_line([]) == "0 sales · revenue Rp 0 · best seller: None"
