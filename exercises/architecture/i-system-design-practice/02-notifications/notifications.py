"""Architecture · I — Notification fan-out, preferences, and dedupe.

One event fans out to each user's ENABLED channels only, and each message is
delivered at most once (dedupe by user + event + channel), because queues
deliver at-least-once.

- event: {"id": str, "type": str, "body": str}
- subscriber: {"user_id": int, "channels": {"email": bool, "push": bool, "sms": bool}}
"""

CHANNEL_ORDER = ("email", "push", "sms")


def fan_out(event: dict, subscribers: list[dict]) -> list[dict]:
    """Return one message per subscriber per ENABLED channel.

    Each message: {"user_id", "channel", "event_id"}.
    Emit channels in CHANNEL_ORDER; skip channels set to False or missing.
    """
    # YOUR CODE HERE
    return []


def deliver_once(sent: set, message: dict) -> str:
    """Deliver a message at most once.

    Key = (user_id, event_id, channel). If already in `sent`, return "duplicate";
    otherwise add it and return "delivered".
    """
    # YOUR CODE HERE
    return ""
