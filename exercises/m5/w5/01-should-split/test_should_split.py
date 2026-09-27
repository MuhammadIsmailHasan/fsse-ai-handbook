"""Checks for should_split.py. Don't edit this file."""

from should_split import should_extract_service


def test_no_signals_means_no_split():
    assert should_extract_service({}) == (False, [])


def test_one_signal_is_not_enough():
    assert should_extract_service({"different_scaling_needs": True}) == (
        False,
        ["different scaling needs"],
    )


def test_two_signals_recommend_a_split():
    ok, reasons = should_extract_service(
        {"different_scaling_needs": True, "clear_data_boundary": True}
    )
    assert ok is True
    assert reasons == ["different scaling needs", "a clear data boundary"]


def test_all_four_signals():
    ok, reasons = should_extract_service(
        {
            "different_scaling_needs": True,
            "separate_team_owns_it": True,
            "different_release_cadence": True,
            "clear_data_boundary": True,
        }
    )
    assert ok is True
    assert reasons == [
        "different scaling needs",
        "a separate team owns it",
        "different release speed",
        "a clear data boundary",
    ]


def test_guard_blocks_split_even_with_signals():
    ok, reasons = should_extract_service(
        {
            "still_finding_boundaries": True,
            "different_scaling_needs": True,
            "clear_data_boundary": True,
        }
    )
    assert ok is False
    assert reasons == ["monolith first: still finding the boundaries"]


def test_reason_order_is_fixed_not_input_order():
    # Signals given in a different order; reasons still come back in REASONS order.
    ok, reasons = should_extract_service(
        {"clear_data_boundary": True, "different_scaling_needs": True}
    )
    assert ok is True
    assert reasons == ["different scaling needs", "a clear data boundary"]


def test_false_signals_are_ignored():
    assert should_extract_service(
        {"different_scaling_needs": True, "separate_team_owns_it": False}
    ) == (False, ["different scaling needs"])
