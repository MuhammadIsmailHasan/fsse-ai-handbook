"""Reference solution."""

import time


class PaymentRejected(Exception):
    def __init__(self, status: int, body: dict):
        super().__init__(f"payment rejected with status {status}")
        self.status, self.body = status, body


class ProviderUnavailable(Exception):
    pass


class PaymentClient:
    URL = "https://api.bayarkita.test/v1/charges"
    TIMEOUT_SECONDS = 10

    def __init__(self, api_key, transport, sleep=time.sleep, max_attempts=3, base_delay=0.5):
        self._api_key = api_key
        self._transport = transport
        self._sleep = sleep
        self._max_attempts = max_attempts
        self._base_delay = base_delay

    def create_charge(self, order_reference: str, amount: int) -> dict:
        if amount <= 0:
            raise ValueError("amount must be positive")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Idempotency-Key": f"charge-{order_reference}",  # the same key on every retry
        }
        payload = {"order_reference": order_reference, "amount": amount}

        for attempt in range(1, self._max_attempts + 1):
            try:
                status, body = self._transport("POST", self.URL, json=payload, headers=headers, timeout=self.TIMEOUT_SECONDS)
            except (TimeoutError, ConnectionError):
                pass  # transient → retry
            else:
                if 200 <= status < 300:
                    return body
                if 400 <= status < 500 and status != 429:
                    raise PaymentRejected(status, body)  # our request is wrong; retrying won't help
                # 429 or 5xx → transient → retry

            if attempt < self._max_attempts:
                self._sleep(self._base_delay * 2 ** (attempt - 1))

        raise ProviderUnavailable(f"BayarKita unavailable after {self._max_attempts} attempts")
