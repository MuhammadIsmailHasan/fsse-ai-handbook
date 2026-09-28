import pytest

from queue_worker import Queue, consume_idempotently, process_with_retries


def test_queue_is_fifo():
    q = Queue()
    assert q.dequeue() is None
    q.enqueue({"id": "a"})
    q.enqueue({"id": "b"})
    assert len(q) == 2
    assert q.dequeue() == {"id": "a"}  # oldest first
    assert q.dequeue() == {"id": "b"}
    assert q.dequeue() is None


def test_idempotent_consumer_skips_duplicates():
    processed: set = set()
    sent = []

    def handler(msg):
        sent.append(msg["id"])

    msg = {"id": "receipt_42", "type": "send_receipt"}
    assert consume_idempotently(processed, handler, msg) == "processed"
    # At-least-once delivery replays the same message:
    assert consume_idempotently(processed, handler, msg) == "duplicate"
    # The handler ran only once — no duplicate receipt.
    assert sent == ["receipt_42"]


def test_retries_then_succeeds():
    attempts_seen = {"n": 0}

    def flaky(msg):
        attempts_seen["n"] += 1
        if attempts_seen["n"] < 3:
            raise RuntimeError("temporary failure")
        # succeeds on the 3rd attempt

    status, attempts = process_with_retries(flaky, {"id": "x"}, max_attempts=5)
    assert status == "done"
    assert attempts == 3


def test_permanent_failure_goes_to_dead_letter():
    def always_fails(msg):
        raise RuntimeError("bad data")

    status, attempts = process_with_retries(always_fails, {"id": "poison"}, max_attempts=3)
    assert status == "dead-letter"
    assert attempts == 3  # tried the full limit, then gave up
