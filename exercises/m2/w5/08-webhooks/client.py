"""M2 · W5 · 08 — Resilient outbound payment client."""

import time


class PaymentRejected(Exception):
    def __init__(self, status: int, body: dict):
        super().__init__(f"payment rejected with status {status}")
        self.status, self.body = status, body


class ProviderUnavailable(Exception):
    pass


class PaymentClient:
    # YOUR CODE HERE
    def __init__(self, api_key, transport, sleep=time.sleep, max_attempts=3, base_delay=0.5):
        pass

    def create_charge(self, order_reference: str, amount: int) -> dict:
        raise NotImplementedError
