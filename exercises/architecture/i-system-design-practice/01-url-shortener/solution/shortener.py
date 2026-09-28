"""Architecture · I — Base62 short codes and a capacity estimate (solution)."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
SECONDS_PER_MONTH = 30 * 86_400


def encode_base62(n: int) -> str:
    if n == 0:
        return "0"
    digits = []
    while n > 0:
        digits.append(ALPHABET[n % 62])
        n //= 62
    return "".join(reversed(digits))


def decode_base62(code: str) -> int:
    n = 0
    for ch in code:
        n = n * 62 + ALPHABET.index(ch)
    return n


def writes_per_sec(monthly_links: int) -> float:
    return monthly_links / SECONDS_PER_MONTH


def capacity(code_len: int) -> int:
    return 62 ** code_len
