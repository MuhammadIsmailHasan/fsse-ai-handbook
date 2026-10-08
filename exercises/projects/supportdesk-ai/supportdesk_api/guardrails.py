"""Guardrails — checkpoint C4. You built these in Module 7 week 2 (exercise 03); reuse or adapt them.

redact_pii(text)        emails -> [EMAIL]; Luhn-valid card numbers (13-19 digits, single spaces/dashes allowed) -> [CARD];
                        Indonesian phone numbers (+62 or 0, then 8, then 7-11 digits, spaces/dashes allowed) -> [PHONE].
                        Anything else is unchanged (a 16-digit ORDER number that fails Luhn stays).
injection_signals(text) names of the prompt-injection patterns found, in this fixed order:
                        "ignore_instructions", "reveal_prompt", "role_change", "fake_system"
"""


def redact_pii(text: str) -> str:
    raise NotImplementedError("C4")


def injection_signals(text: str) -> list[str]:
    raise NotImplementedError("C4")
