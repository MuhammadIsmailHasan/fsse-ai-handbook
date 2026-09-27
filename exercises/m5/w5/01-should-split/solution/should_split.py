"""Reference solution. See README.md."""

# Real, independent signals → their reason text, in a fixed order.
REASONS = {
    "different_scaling_needs": "different scaling needs",
    "separate_team_owns_it": "a separate team owns it",
    "different_release_cadence": "different release speed",
    "clear_data_boundary": "a clear data boundary",
}


def should_extract_service(signals: dict) -> tuple[bool, list[str]]:
    # Monolith first: never split while the boundaries are still unclear.
    if signals.get("still_finding_boundaries"):
        return (False, ["monolith first: still finding the boundaries"])

    # Collect a reason for every real signal that is true, in REASONS order.
    reasons = [text for key, text in REASONS.items() if signals.get(key)]

    # Split only with at least two independent reasons.
    return (len(reasons) >= 2, reasons)
