"""Architecture · I — Notification fan-out, preferences, and dedupe (solution)."""

CHANNEL_ORDER = ("email", "push", "sms")


def fan_out(event: dict, subscribers: list[dict]) -> list[dict]:
    messages = []
    for sub in subscribers:
        channels = sub.get("channels", {})
        for channel in CHANNEL_ORDER:
            if channels.get(channel):
                messages.append(
                    {"user_id": sub["user_id"], "channel": channel, "event_id": event["id"]}
                )
    return messages


def deliver_once(sent: set, message: dict) -> str:
    key = (message["user_id"], message["event_id"], message["channel"])
    if key in sent:
        return "duplicate"
    sent.add(key)
    return "delivered"
