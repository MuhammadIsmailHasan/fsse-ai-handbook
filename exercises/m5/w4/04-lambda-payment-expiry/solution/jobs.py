"""Lambda handlers for expiring unpaid payments. See README.md."""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)
SAFETY_MARGIN_MS = 5000


@dataclass
class Deps:
    repository: Any
    sqs: Any
    queue_url: str
    clock: Callable[[], datetime]


def scan_handler(event: dict, context: Any, deps: Deps) -> dict:
    ids = deps.repository.find_expired_pending(deps.clock(), limit=500)
    for start in range(0, len(ids), 10):
        batch = ids[start : start + 10]
        response = deps.sqs.send_message_batch(
            QueueUrl=deps.queue_url,
            Entries=[{"Id": str(i), "MessageBody": json.dumps({"payment_id": pid})} for i, pid in enumerate(batch)],
        )
        if response.get("Failed"):
            raise RuntimeError(f"failed to enqueue {len(response['Failed'])} messages")  # retry the whole scan
    return {"found": len(ids), "enqueued": len(ids)}


def _payment_id(body: str) -> int | None:
    try:
        data = json.loads(body)
    except (TypeError, ValueError):
        return None
    value = data.get("payment_id") if isinstance(data, dict) else None
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def expire_handler(event: dict, context: Any, deps: Deps) -> dict:
    records = event.get("Records", [])
    failures: list[dict] = []
    expired = skipped = 0
    for index, record in enumerate(records):
        if context.get_remaining_time_in_millis() < SAFETY_MARGIN_MS:
            # Hand the rest back to SQS instead of being killed halfway through an update.
            failures.extend({"itemIdentifier": r["messageId"]} for r in records[index:])
            break
        payment_id = _payment_id(record.get("body", ""))
        if payment_id is None:
            logger.error("poison message %s skipped", record.get("messageId"))
            skipped += 1
            continue
        try:
            outcome = deps.repository.expire(payment_id, deps.clock())
        except Exception:
            logger.exception("expiring payment %s failed", payment_id)
            failures.append({"itemIdentifier": record["messageId"]})
            continue
        if outcome == "expired":
            expired += 1
        else:
            skipped += 1
    return {"batchItemFailures": failures, "expired": expired, "skipped": skipped}
