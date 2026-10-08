"""Module 7 · W2 — Guardrails around a model (no API key needed).

A guardrail is a check that your CODE runs before the model sees something, after the model answers,
and before a tool does something risky. None of them is perfect; together they make the system safer.
"""

import re  # noqa: F401  (you will want it)


def luhn_valid(digits: str) -> bool:
    """The Luhn check used by payment card numbers.
    Starting from the RIGHT, double every second digit; if the double is above 9 subtract 9; the sum must be a multiple of 10.
    `digits` contains only the characters 0-9."""
    raise NotImplementedError


def redact_pii(text: str) -> str:
    """Replace personal data with placeholders (apply in this order):
      - email addresses                                   -> [EMAIL]
      - card numbers: 13 to 19 digits, optionally written with single spaces or dashes between digits,
        AND passing luhn_valid                            -> [CARD]
      - Indonesian phone numbers: +62 or 0 followed by 8 and then 7 to 11 more digits
        (like 081234567890 or +6281234567890; spaces/dashes between digits are allowed) -> [PHONE]
    Leave everything else unchanged. A long number that fails the Luhn check (an order number) stays as it is."""
    raise NotImplementedError


def injection_signals(text: str) -> list[str]:
    """Return the NAMES of the prompt-injection patterns found in text (case-insensitive), in this fixed order:
      "ignore_instructions"   e.g. "ignore previous instructions", "ignore all the above instructions", "disregard your rules"
      "reveal_prompt"         e.g. "reveal your system prompt", "show me your instructions", "print your prompt"
      "role_change"           e.g. "you are now", "act as", "pretend to be"
      "fake_system"           a line that starts with "system:" or contains "<system>"
    An empty list means nothing suspicious. (This is a weak signal, not a wall: use it to log and to be more careful.)"""
    raise NotImplementedError


def check_output(text: str, secrets: list[str], max_chars: int = 2000) -> list[str]:
    """Problems with a model answer, in this order:
      "leaks_secret"   if any of `secrets` (non-empty strings) appears in text (case-sensitive)
      "too_long"       if len(text) > max_chars
      "has_pii"        if redact_pii(text) != text
    Return the list of problem names (empty = fine)."""
    raise NotImplementedError


def authorize(tool_name: str, args: dict, policy: dict) -> str:
    """Decide if a tool call may run. Returns "allow", "needs_approval" or "deny".

    policy = {
        "allowed": {"get_order", "issue_refund"},                 # any tool not listed -> "deny"
        "approval_over": {"issue_refund": {"amount": 100000}},    # a number argument ABOVE the limit -> "needs_approval"
        "always_approve": {"delete_account"},                     # always "needs_approval" (if allowed)
    }
    Rules in order: not in allowed -> deny; in always_approve -> needs_approval; any limit in approval_over[tool]
    exceeded (arg is a number and arg > limit) -> needs_approval; an argument that should be a number but is
    not (bool, str, None, missing) -> deny (do not guess); otherwise allow.
    "approval_over" and "always_approve" may be missing from the policy."""
    raise NotImplementedError
