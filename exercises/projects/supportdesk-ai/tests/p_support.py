"""Fakes and helpers for the SupportDesk acceptance tests. Don't edit this file."""

import hashlib
import re
import time
from contextlib import contextmanager

import jwt

TEST_SECRET = "acceptance-tests-only-" + "x" * 32

ARTICLES = {
    "refund-policy": {
        "id": "refund-policy",
        "title": "Refund policy",
        "lang": "en",
        "body": (
            "General information about returns at Warung Kita Online.\n\n"
            "## Refund timing\n"
            "Refunds are paid back within 7 days after we receive the returned item.\n\n"
            "## Refund conditions\n"
            "Items must be unused and returned within 14 days of delivery."
        ),
    },
    "shipping": {
        "id": "shipping",
        "title": "Shipping and delivery",
        "lang": "en",
        "body": (
            "## Shipping costs\n"
            "Shipping is free for orders above Rp 200.000 within Java. Delivery to Papua costs Rp 50.000.\n\n"
            "## Delivery time\n"
            "Delivery takes 2 to 5 days within Java."
        ),
    },
    "account-security": {
        "id": "account-security",
        "title": "Account security",
        "lang": "en",
        "body": "## Reset password\nUse the reset password link on the login page. The link expires after 30 minutes.",
    },
    "kebijakan-retur": {
        "id": "kebijakan-retur",
        "title": "Kebijakan retur",
        "lang": "id",
        "body": "## Waktu refund\nRefund dibayarkan dalam 7 hari setelah barang retur kami terima.",
    },
}

ORDERS = {
    "ORD-1001": {"id": "ORD-1001", "owner": "user-1", "status": "shipped", "eta": "2026-10-12"},
    "ORD-2002": {"id": "ORD-2002", "owner": "user-2", "status": "packed", "eta": "2026-10-15"},
}


def make_token(sub="user-1", role=None, secret=TEST_SECRET, expires_in=3600, **claims) -> str:
    payload = {"exp": int(time.time()) + expires_in, **claims}
    if sub is not None:
        payload["sub"] = sub
    if role:
        payload["role"] = role
    return jwt.encode(payload, secret, algorithm="HS256")


def bearer(token) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---- model replies (the shapes of the real API)

def text(t: str) -> dict:
    return {"stop_reason": "end_turn", "content": [{"type": "text", "text": t}]}


def tool_call(name: str, input: dict | None = None, id: str = "toolu_1") -> dict:
    return {"stop_reason": "tool_use", "content": [{"type": "tool_use", "id": id, "name": name, "input": input or {}}]}


class FakeLLM:
    """Plays the model: returns scripted replies in order, and records every call it receives."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls: list[dict] = []

    def complete(self, system, messages, tools):
        self.calls.append({"system": system, "messages": [dict(m) for m in messages], "tools": tools})
        if self.replies:
            return self.replies.pop(0)
        return text("(no more scripted replies)")

    @property
    def everything_sent(self) -> str:
        """All text the model was given across all calls (system + messages + tool results), as one string."""
        parts = []
        for call in self.calls:
            parts.append(call["system"] or "")
            for message in call["messages"]:
                content = message["content"]
                parts.append(content if isinstance(content, str) else repr(content))
        return "\n".join(parts)


_STOP = {"a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "in", "on", "at", "for", "and", "or", "it",
         "this", "that", "with", "as", "by", "from", "we", "you", "your", "our", "can", "will", "after", "how", "do",
         "does", "what", "when", "where", "i", "my", "me", "if", "within"}


class HashEmbedder:
    """A deterministic bag-of-words embedder (content words only, trailing 's' removed)."""

    dim = 256

    def embed(self, texts):
        return [self._one(t) for t in texts]

    def _one(self, text):
        vector = [0.0] * self.dim
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            if token in _STOP:
                continue
            if token.endswith("s") and len(token) > 3:
                token = token[:-1]
            h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            vector[h % self.dim] += 1.0 if (h >> 20) & 1 else -1.0
        norm = sum(x * x for x in vector) ** 0.5
        return [x / norm for x in vector] if norm else vector


class FakeOrders:
    def __init__(self, orders=None):
        self.orders = dict(ORDERS if orders is None else orders)
        self.lookups: list[str] = []

    def get_order(self, order_id):
        self.lookups.append(order_id)
        return self.orders.get(order_id)


class _Handle:
    def __init__(self, attrs):
        self.attrs = attrs

    def set(self, **attrs):
        self.attrs.update(attrs)


class FakeTracer:
    """Records every span as (name, attrs) in the order the spans were opened."""

    def __init__(self):
        self.spans: list[tuple[str, dict]] = []

    @contextmanager
    def span(self, name, /, **attrs):
        record = (name, dict(attrs))
        self.spans.append(record)
        handle = _Handle(record[1])
        yield handle

    @property
    def names(self):
        return [name for name, _ in self.spans]
