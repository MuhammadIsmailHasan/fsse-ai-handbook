import re


def luhn_valid(digits):
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_CARD = re.compile(r"(?<![\d])\d(?:[ -]?\d){12,18}(?![\d])")
_PHONE = re.compile(r"(?<![\d+])(?:\+62|0)8(?:[ -]?\d){7,11}(?![\d])")


def redact_pii(text):
    text = _EMAIL.sub("[EMAIL]", text)

    def card(match):
        digits = re.sub(r"[ -]", "", match.group(0))
        return "[CARD]" if 13 <= len(digits) <= 19 and luhn_valid(digits) else match.group(0)

    text = _CARD.sub(card, text)
    return _PHONE.sub("[PHONE]", text)


_RULES = [
    ("ignore_instructions", re.compile(r"\b(ignore|disregard|forget)\b.{0,30}\b(instructions|rules|prompt|above)\b", re.I)),
    ("reveal_prompt", re.compile(r"\b(reveal|show|print|repeat|display)\b.{0,25}\b(system prompt|instructions|prompt)\b", re.I)),
    ("role_change", re.compile(r"\b(you are now|act as|pretend to be)\b", re.I)),
    ("fake_system", re.compile(r"(^\s*system\s*:|<system>)", re.I | re.M)),
]


def injection_signals(text):
    return [name for name, pattern in _RULES if pattern.search(text)]


def check_output(text, secrets, max_chars=2000):
    problems = []
    if any(s and s in text for s in secrets):
        problems.append("leaks_secret")
    if len(text) > max_chars:
        problems.append("too_long")
    if redact_pii(text) != text:
        problems.append("has_pii")
    return problems


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def authorize(tool_name, args, policy):
    if tool_name not in policy.get("allowed", set()):
        return "deny"
    if tool_name in policy.get("always_approve", set()):
        return "needs_approval"
    needs = False
    for arg, limit in policy.get("approval_over", {}).get(tool_name, {}).items():
        value = args.get(arg)
        if not _is_number(value):
            return "deny"
        if value > limit:
            needs = True
    return "needs_approval" if needs else "allow"
