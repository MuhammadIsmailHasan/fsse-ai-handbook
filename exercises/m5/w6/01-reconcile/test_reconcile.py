"""Checks for reconcile.py. Don't edit this file."""

from reconcile import reconcile


def test_start_missing_pods():
    assert reconcile(3, 2) == {"action": "start", "count": 1}


def test_stop_extra_pods():
    assert reconcile(3, 5) == {"action": "stop", "count": 2}


def test_already_matches():
    assert reconcile(3, 3) == {"action": "none", "count": 0}


def test_start_from_zero():
    assert reconcile(4, 0) == {"action": "start", "count": 4}


def test_scale_all_the_way_down():
    assert reconcile(0, 3) == {"action": "stop", "count": 3}
