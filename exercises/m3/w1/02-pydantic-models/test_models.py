import pytest
from pydantic import ValidationError

from models import Product, Signup


def test_product_valid_and_coercion():
    p = Product(name="Mug", price="50000", stock="3")  # numeric strings coerce
    assert p.name == "Mug"
    assert p.price == 50000.0
    assert p.stock == 3


def test_product_defaults_stock():
    p = Product(name="Mug", price=10)
    assert p.stock == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": "", "price": 10},          # name too short
        {"name": "x" * 51, "price": 10},    # name too long
        {"name": "Mug", "price": 0},        # price must be > 0
        {"name": "Mug", "price": -5},
        {"name": "Mug", "price": 10, "stock": -1},  # stock must be >= 0
    ],
)
def test_product_rejects_bad_values(kwargs):
    with pytest.raises(ValidationError):
        Product(**kwargs)


def test_signup_normalizes_email():
    s = Signup(email="ISMAIL@Example.com", password="longenough")
    assert s.email == "ismail@example.com"  # lowercased by the validator


def test_signup_rejects_bad_email_and_short_password():
    with pytest.raises(ValidationError):
        Signup(email="no-at-sign", password="longenough")
    with pytest.raises(ValidationError):
        Signup(email="a@b.com", password="short")
