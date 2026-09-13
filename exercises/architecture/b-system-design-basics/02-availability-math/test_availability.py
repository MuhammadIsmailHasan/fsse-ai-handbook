import pytest

from availability import copies_needed, downtime_minutes_per_year, parallel, series


def test_downtime():
    assert downtime_minutes_per_year(0.999) == pytest.approx(525.6)
    assert downtime_minutes_per_year(1.0) == pytest.approx(0)


def test_series():
    assert series([0.999, 0.999]) == pytest.approx(0.998001)
    assert series([0.999, 0.999, 0.999]) == pytest.approx(0.997003, rel=1e-6)
    assert series([]) == 1.0


def test_parallel():
    assert parallel([0.99, 0.99]) == pytest.approx(0.9999)
    assert parallel([0.9, 0.8]) == pytest.approx(0.98)
    assert parallel([]) == 0.0


def test_copies_needed():
    assert copies_needed(0.99, 0.9999) == 2
    assert copies_needed(0.9, 0.99999) == 5
    assert copies_needed(0.999, 0.99) == 1


@pytest.mark.parametrize("single", [0, 1, 1.5, -0.1])
def test_copies_needed_validates(single):
    with pytest.raises(ValueError):
        copies_needed(single, 0.99)
