"""Checks for jobs.py (SQS mocked with moto). Don't edit this file."""

import json
from datetime import datetime, timezone

import boto3
import pytest
from moto import mock_aws

from jobs import Deps, expire_handler, scan_handler

NOW = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")


class FakeRepository:
    def __init__(self, expired=(), outcomes=None):
        self.expired, self.outcomes, self.calls, self.scans = list(expired), outcomes or {}, [], []

    def find_expired_pending(self, now, limit):
        self.scans.append((now, limit))
        return self.expired[:limit]

    def expire(self, payment_id, now):
        self.calls.append(payment_id)
        outcome = self.outcomes.get(payment_id, "expired")
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeContext:
    def __init__(self, remaining):
        self.remaining = list(remaining)

    def get_remaining_time_in_millis(self):
        return self.remaining.pop(0) if len(self.remaining) > 1 else self.remaining[0]


def drain(sqs, url):
    bodies = []
    while True:
        messages = sqs.receive_message(QueueUrl=url, MaxNumberOfMessages=10).get("Messages", [])
        if not messages:
            return bodies
        for message in messages:
            bodies.append(json.loads(message["Body"]))
            sqs.delete_message(QueueUrl=url, ReceiptHandle=message["ReceiptHandle"])


@mock_aws
def test_scan_enqueues_in_batches_of_ten():
    sqs = boto3.client("sqs", region_name="ap-southeast-1")
    url = sqs.create_queue(QueueName="revoshop-payment-expiry")["QueueUrl"]
    repository = FakeRepository(expired=list(range(1, 24)))
    calls = []
    real_batch = sqs.send_message_batch

    def spy(**kwargs):
        calls.append([e["Id"] for e in kwargs["Entries"]])
        return real_batch(**kwargs)

    sqs.send_message_batch = spy
    result = scan_handler({"source": "aws.scheduler"}, None, Deps(repository, sqs, url, lambda: NOW))
    assert result == {"found": 23, "enqueued": 23}
    assert repository.scans == [(NOW, 500)]
    assert calls == [[str(i) for i in range(10)], [str(i) for i in range(10)], ["0", "1", "2"]]
    assert sorted(b["payment_id"] for b in drain(sqs, url)) == list(range(1, 24))


def test_scan_nothing_to_do_and_failed_entries():
    class NoCalls:
        def send_message_batch(self, **kwargs):
            raise AssertionError("should not be called")

    assert scan_handler({}, None, Deps(FakeRepository(), NoCalls(), "url", lambda: NOW)) == {"found": 0, "enqueued": 0}

    class Flaky:
        def send_message_batch(self, **kwargs):
            return {"Successful": [{"Id": "0"}], "Failed": [{"Id": "1", "Code": "InternalError", "SenderFault": False}]}

    with pytest.raises(RuntimeError):
        scan_handler({}, None, Deps(FakeRepository(expired=[1, 2]), Flaky(), "url", lambda: NOW))


def records(*bodies):
    return {"Records": [{"messageId": f"m{i}", "body": body} for i, body in enumerate(bodies)]}


def test_expire_handler_partial_batch_response():
    repository = FakeRepository(outcomes={2: "already_final", 3: RuntimeError("deadlock detected")})
    event = records(
        json.dumps({"payment_id": 1}),
        json.dumps({"payment_id": 2}),
        json.dumps({"payment_id": 3}),
        "not json",
        json.dumps({"payment_id": "4"}),
        json.dumps([5]),
        json.dumps({"payment_id": 6}),
    )
    result = expire_handler(event, FakeContext([60_000]), Deps(repository, None, "url", lambda: NOW))
    assert result == {"batchItemFailures": [{"itemIdentifier": "m2"}], "expired": 2, "skipped": 4}
    assert repository.calls == [1, 2, 3, 6]


def test_expire_handler_stops_before_timeout():
    repository = FakeRepository()
    event = records(*(json.dumps({"payment_id": i}) for i in range(5)))
    result = expire_handler(event, FakeContext([30_000, 20_000, 4_999, 60_000]), Deps(repository, None, "url", lambda: NOW))
    assert result["batchItemFailures"] == [{"itemIdentifier": "m2"}, {"itemIdentifier": "m3"}, {"itemIdentifier": "m4"}]
    assert repository.calls == [0, 1]
    assert result["expired"] == 2
    assert expire_handler({"Records": []}, FakeContext([100]), Deps(repository, None, "url", lambda: NOW)) == {"batchItemFailures": [], "expired": 0, "skipped": 0}
