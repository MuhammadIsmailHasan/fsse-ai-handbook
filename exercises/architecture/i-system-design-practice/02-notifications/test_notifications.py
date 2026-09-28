from notifications import deliver_once, fan_out

EVENT = {"id": "evt_1", "type": "order_shipped", "body": "Your order shipped"}

SUBSCRIBERS = [
    {"user_id": 1, "channels": {"email": True, "push": True, "sms": False}},
    {"user_id": 2, "channels": {"email": False, "push": False, "sms": True}},
    {"user_id": 3, "channels": {}},  # opted out of everything
]


def test_fan_out_respects_preferences_and_order():
    messages = fan_out(EVENT, SUBSCRIBERS)
    assert messages == [
        {"user_id": 1, "channel": "email", "event_id": "evt_1"},
        {"user_id": 1, "channel": "push", "event_id": "evt_1"},
        {"user_id": 2, "channel": "sms", "event_id": "evt_1"},
    ]
    # User 3 (all off) gets nothing; user 1's disabled sms is skipped.


def test_deliver_once_dedupes_redelivery():
    sent: set = set()
    messages = fan_out(EVENT, SUBSCRIBERS)
    # First pass: everything delivers.
    assert [deliver_once(sent, m) for m in messages] == ["delivered", "delivered", "delivered"]
    # The event is redelivered (at-least-once): all are duplicates now.
    assert [deliver_once(sent, m) for m in messages] == ["duplicate", "duplicate", "duplicate"]


def test_dedupe_is_per_channel_and_per_event():
    sent: set = set()
    m_email = {"user_id": 1, "channel": "email", "event_id": "evt_1"}
    m_push = {"user_id": 1, "channel": "push", "event_id": "evt_1"}
    m_other_event = {"user_id": 1, "channel": "email", "event_id": "evt_2"}
    assert deliver_once(sent, m_email) == "delivered"
    assert deliver_once(sent, m_push) == "delivered"       # different channel, ok
    assert deliver_once(sent, m_other_event) == "delivered"  # different event, ok
    assert deliver_once(sent, m_email) == "duplicate"       # same trio → blocked
