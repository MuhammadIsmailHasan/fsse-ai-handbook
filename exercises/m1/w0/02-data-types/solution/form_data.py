"""Reference solution — compare AFTER a real attempt."""


def parse_age(text: str) -> int:
    return int(text.strip())


def parse_height_m(text: str) -> float:
    # float() first, because heights like "165.5" contain decimals
    return float(text.strip()) / 100


def parse_newsletter(text: str) -> bool:
    return text.strip().lower() in ("yes", "y", "true")


def describe_user(name: str, age: int) -> str:
    return f"{name} ({age} years old)"


def parse_price_idr(text: str) -> int:
    """Stretch goal: "Rp 15.000" -> 15000"""
    digits = text.replace("Rp", "").replace(".", "").replace(",", "").strip()
    return int(digits)
