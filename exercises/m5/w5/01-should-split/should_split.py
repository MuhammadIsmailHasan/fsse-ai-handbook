"""Decide whether to extract a piece of a monolith into its own service.

See README.md for the rules. Return (recommend_split, reasons).
"""


def should_extract_service(signals: dict) -> tuple[bool, list[str]]:
    raise NotImplementedError
