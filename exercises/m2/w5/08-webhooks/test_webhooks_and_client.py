"""Webhook security/idempotency on PostgreSQL + a resilient client with a fake transport. Don't edit."""

import hashlib
import hmac
import json

import pytest
from sqlalchemy import func, select

from app import create_app
from client import PaymentClient, PaymentRejected, ProviderUnavailable
from models import Order, WebhookEvent, db
from signatures import InvalidSignature, verify_signature

SECRET = "whsec_test_only_1234567890"
NOW = 1_789_000_000.0


def sign(body: bytes, timestamp: float = NOW, secret: str = SECRET) -> str:
    digest = hmac.new(secret.encode(), f"{int(timestamp)}.".encode() + body, hashlib.sha256).hexdigest()
    return f"t={int(timestamp)},v1={digest}"


# ---- signatures ----------------------------------------------------------------------


def test_valid_signature():
    body = b'{"id": "evt_1"}'
    verify_signature(body, sign(body), SECRET, now=NOW)


@pytest.mark.parametrize(
    "header",
    [None, "", "garbage", "t=abc,v1=00", f"t={int(NOW)}", sign(b"other body"), sign(b'{"id": "evt_1"}', secret="wrong")],
)
def test_invalid_signatures(header):
    with pytest.raises(InvalidSignature):
        verify_signature(b'{"id": "evt_1"}', header, SECRET, now=NOW)


def test_replay_window_both_directions():
    body = b"{}"
    verify_signature(body, sign(body, timestamp=NOW - 300), SECRET, now=NOW)
    with pytest.raises(InvalidSignature):
        verify_signature(body, sign(body, timestamp=NOW - 301), SECRET, now=NOW)
    with pytest.raises(InvalidSignature):
        verify_signature(body, sign(body, timestamp=NOW + 301), SECRET, now=NOW)


def test_uses_constant_time_comparison():
    from pathlib import Path

    assert "compare_digest" in Path(__file__).with_name("signatures.py").read_text()


# ---- webhook endpoint ------------------------------------------------------------------


@pytest.fixture
def app(pg_url):
    app = create_app(pg_url, clock=lambda: NOW)
    with app.app_context():
        db.create_all()
        db.session.add(Order(reference="ORD-1", amount=150_000))
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def post_event(client, event_id="evt_1", type_="payment.paid", reference="ORD-1", amount=150_000, raw=None, header=None):
    body = raw if raw is not None else json.dumps({"id": event_id, "type": type_, "data": {"order_reference": reference, "amount": amount}}).encode()
    headers = {"Content-Type": "application/json", "X-BayarKita-Signature": header if header is not None else sign(body)}
    return client.post("/webhooks/bayarkita", data=body, headers=headers)


def order_state(app):
    with app.app_context():
        order = db.session.scalars(select(Order)).one()
        return order.payment_status, order.paid_at


def events(app):
    with app.app_context():
        return db.session.scalar(select(func.count()).select_from(WebhookEvent))


def test_paid_event_processed(client, app):
    response = post_event(client)
    assert response.status_code == 200 and response.get_json() == {"status": "processed"}
    status, paid_at = order_state(app)
    assert status == "paid" and paid_at is not None and paid_at.timestamp() == NOW
    assert events(app) == 1


def test_bad_signature_changes_nothing(client, app):
    response = post_event(client, header=sign(b"tampered"))
    assert response.status_code == 401 and response.get_json()["error"]["code"] == "invalid_signature"
    forged = post_event(client, header="")
    assert forged.status_code == 401
    assert order_state(app)[0] == "pending" and events(app) == 0


def test_signature_checked_on_raw_bytes(client, app):
    compact = b'{"id":"evt_raw","type":"payment.paid","data":{"order_reference":"ORD-1","amount":150000}}'
    assert post_event(client, raw=compact, header=sign(compact)).get_json() == {"status": "processed"}


def test_invalid_payload_after_valid_signature(client):
    for raw in (b"not json", b'{"type": "payment.paid"}', b'{"id": "evt_x", "type": "payment.paid", "data": {}}'):
        response = post_event(client, raw=raw, header=sign(raw))
        assert response.status_code == 400 and response.get_json()["error"]["code"] == "invalid_payload"


def test_duplicate_delivery(client, app):
    post_event(client)
    again = post_event(client)
    assert again.status_code == 200 and again.get_json() == {"status": "duplicate"}
    assert events(app) == 1


def test_out_of_order_and_refund(client, app):
    assert post_event(client, "evt_paid").get_json() == {"status": "processed"}
    late_pending = post_event(client, "evt_pending", type_="payment.pending")
    assert late_pending.get_json() == {"status": "stale"}
    assert order_state(app)[0] == "paid"
    assert post_event(client, "evt_refund", type_="payment.refunded").get_json() == {"status": "processed"}
    assert post_event(client, "evt_paid_again", type_="payment.paid").get_json() == {"status": "stale"}
    assert order_state(app)[0] == "refunded" and events(app) == 4


def test_ignored_and_mismatched(client, app):
    assert post_event(client, "evt_type", type_="customer.updated").get_json() == {"status": "ignored"}
    assert post_event(client, "evt_unknown", reference="ORD-404").get_json() == {"status": "ignored"}
    assert post_event(client, "evt_amount", amount=1).get_json() == {"status": "amount_mismatch"}
    assert order_state(app)[0] == "pending" and events(app) == 3


# ---- outbound client -------------------------------------------------------------------


class FakeTransport:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def __call__(self, method, url, json=None, headers=None, timeout=None):
        self.calls.append({"method": method, "url": url, "json": json, "headers": headers, "timeout": timeout})
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def make_client(outcomes):
    transport, sleeps = FakeTransport(outcomes), []
    return PaymentClient("sk_test", transport, sleep=sleeps.append), transport, sleeps


def test_success_first_try():
    client, transport, sleeps = make_client([(201, {"id": "ch_1"})])
    assert client.create_charge("ORD-1", 150_000) == {"id": "ch_1"}
    call = transport.calls[0]
    assert call["method"] == "POST" and call["url"] == "https://api.bayarkita.test/v1/charges"
    assert call["json"] == {"order_reference": "ORD-1", "amount": 150_000}
    assert call["headers"] == {"Authorization": "Bearer sk_test", "Idempotency-Key": "charge-ORD-1"}
    assert call["timeout"] == 10 and sleeps == []


def test_retries_transient_failures_with_backoff_and_same_key():
    client, transport, sleeps = make_client([TimeoutError(), (503, {}), (200, {"id": "ch_2"})])
    assert client.create_charge("ORD-2", 1000) == {"id": "ch_2"}
    assert sleeps == [0.5, 1.0]
    assert {c["headers"]["Idempotency-Key"] for c in transport.calls} == {"charge-ORD-2"}


def test_rate_limit_is_retried():
    client, transport, _ = make_client([(429, {}), (200, {"id": "ch_3"})])
    assert client.create_charge("ORD-3", 1000)["id"] == "ch_3" and len(transport.calls) == 2


def test_client_errors_are_not_retried():
    client, transport, sleeps = make_client([(422, {"error": "invalid amount"})])
    with pytest.raises(PaymentRejected) as info:
        client.create_charge("ORD-4", 1000)
    assert info.value.status == 422 and len(transport.calls) == 1 and sleeps == []


def test_gives_up_after_max_attempts():
    client, transport, sleeps = make_client([ConnectionError(), (500, {}), TimeoutError()])
    with pytest.raises(ProviderUnavailable):
        client.create_charge("ORD-5", 1000)
    assert len(transport.calls) == 3 and sleeps == [0.5, 1.0]


def test_invalid_amount_never_calls_provider():
    client, transport, _ = make_client([])
    with pytest.raises(ValueError):
        client.create_charge("ORD-6", 0)
    assert transport.calls == []
