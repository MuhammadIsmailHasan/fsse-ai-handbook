"""Reference solution."""

import json
from datetime import UTC, datetime

from flask import Blueprint, current_app, request
from sqlalchemy import select

from models import Order, WebhookEvent, db
from signatures import InvalidSignature, verify_signature

webhooks_bp = Blueprint("webhooks", __name__)

STATUS_RANK = {"pending": 1, "paid": 2, "refunded": 3}
EVENT_STATUS = {"payment.pending": "pending", "payment.paid": "paid", "payment.refunded": "refunded"}


def error(status: int, code: str):
    return {"error": {"code": code}}, status


def parse_event(raw_body: bytes) -> dict | None:
    try:
        event = json.loads(raw_body)
        if not isinstance(event, dict):
            return None
        reference = event["data"]["order_reference"]
        if not event.get("id") or not event.get("type") or not reference:
            return None
        return event
    except (ValueError, KeyError, TypeError):
        return None


@webhooks_bp.post("/webhooks/bayarkita")
def bayarkita_webhook():
    raw_body = request.get_data()  # the exact bytes the provider signed
    try:
        verify_signature(
            raw_body,
            request.headers.get("X-BayarKita-Signature"),
            current_app.config["WEBHOOK_SECRET"],
            now=current_app.config["CLOCK"](),
        )
    except InvalidSignature:
        current_app.logger.warning("Rejected webhook with invalid signature")
        return error(401, "invalid_signature")

    event = parse_event(raw_body)
    if event is None:
        return error(400, "invalid_payload")

    existing = db.session.scalar(select(WebhookEvent.id).where(WebhookEvent.provider_event_id == event["id"]))
    if existing is not None:
        return {"status": "duplicate"}, 200

    result = apply_event(event)
    # Recording the event and changing the order happen in ONE commit.
    db.session.add(WebhookEvent(provider_event_id=event["id"], type=event["type"], result=result))
    db.session.commit()
    return {"status": result}, 200


def apply_event(event: dict) -> str:
    new_status = EVENT_STATUS.get(event["type"])
    if new_status is None:
        return "ignored"

    order = db.session.scalars(
        select(Order).where(Order.reference == event["data"]["order_reference"]).with_for_update()
    ).one_or_none()
    if order is None:
        current_app.logger.info("Webhook for unknown order %s", event["data"]["order_reference"])
        return "ignored"
    if event["data"].get("amount") != order.amount:
        return "amount_mismatch"
    if STATUS_RANK[new_status] <= STATUS_RANK[order.payment_status]:
        return "stale"  # late or repeated event: never move backwards

    order.payment_status = new_status
    if new_status == "paid":
        order.paid_at = datetime.fromtimestamp(current_app.config["CLOCK"](), UTC)
    return "processed"
