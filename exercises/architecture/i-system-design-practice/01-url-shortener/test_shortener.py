import pytest

from shortener import capacity, decode_base62, encode_base62, writes_per_sec


def test_encode_small_values():
    assert encode_base62(0) == "0"
    assert encode_base62(1) == "1"
    assert encode_base62(61) == "Z"
    assert encode_base62(62) == "10"
    assert encode_base62(125) == "21"


@pytest.mark.parametrize("n", [0, 1, 61, 62, 125, 1000, 3_500_000, 999_999_999])
def test_round_trip(n):
    assert decode_base62(encode_base62(n)) == n


def test_writes_per_sec():
    # 100M links/month ≈ 38.6 writes/sec
    assert writes_per_sec(100_000_000) == pytest.approx(38.58, rel=1e-3)
    assert writes_per_sec(0) == 0


def test_capacity_of_code_length():
    assert capacity(1) == 62
    assert capacity(7) == 62 ** 7  # ~3.5 trillion links
    assert capacity(7) > 3_000_000_000_000
