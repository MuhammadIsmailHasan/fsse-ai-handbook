"""Architecture · I — Base62 short codes and a capacity estimate.

A URL shortener turns a row's auto-increment id into a short, unique code by
encoding it in base62 (digits, lowercase, uppercase). Because ids are unique,
codes never collide.
"""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 62 chars
SECONDS_PER_MONTH = 30 * 86_400


def encode_base62(n: int) -> str:
    """Encode a non-negative integer as a base62 string. encode(0) == '0'."""
    # YOUR CODE HERE
    return ""


def decode_base62(code: str) -> int:
    """Inverse of encode_base62."""
    # YOUR CODE HERE
    return -1


def writes_per_sec(monthly_links: int) -> float:
    """Average writes per second given links created per month."""
    # YOUR CODE HERE
    return -1.0


def capacity(code_len: int) -> int:
    """How many distinct links a code of this length can address (62**len)."""
    # YOUR CODE HERE
    return -1
