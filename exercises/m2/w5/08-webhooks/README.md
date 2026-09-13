# M2 · W5 · 08 — A Secure Payment Webhook and a Resilient Client

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

**BayarKita** is a fictional payment provider. Provided: `app.py` (factory with `WEBHOOK_SECRET`, injectable `CLOCK`, registers `webhooks.webhooks_bp`) and `models.py` (`Order`, `WebhookEvent`).

## 1. `signatures.py`
`verify_signature(raw_body: bytes, header: str | None, secret: str, now: float, tolerance: int = 300) -> None`
- header format: `t=<unix seconds>,v1=<hex>`; signed payload: `f"{t}.".encode() + raw_body`; `v1 = HMAC-SHA256(secret, payload).hexdigest()`
- raise `InvalidSignature` for: missing/malformed header, timestamp older **or newer** than `tolerance` seconds from `now`, or wrong signature (compare with `hmac.compare_digest`)

## 2. `webhooks.py` — `POST /webhooks/bayarkita`
Event body: `{"id": "evt_1", "type": "payment.paid", "data": {"order_reference": "ORD-1", "amount": 150000}}`

| Situation | Response (JSON) |
|---|---|
| signature invalid (header `X-BayarKita-Signature`) | `401 {"error": {"code": "invalid_signature"}}` — nothing stored |
| valid signature but body not JSON / missing `id`, `type`, `data.order_reference` | `400 {"error": {"code": "invalid_payload"}}` |
| event `id` already processed | `200 {"status": "duplicate"}` — nothing changes |
| type not in `payment.pending`, `payment.paid`, `payment.refunded` | record event → `200 {"status": "ignored"}` |
| unknown `order_reference` | record event → `200 {"status": "ignored"}` |
| `data.amount` ≠ order amount | record event → `200 {"status": "amount_mismatch"}`, order unchanged |
| status would move **backwards** (order `pending` < `paid` < `refunded`) or stay the same | record event → `200 {"status": "stale"}` |
| otherwise | update `payment_status` (and `paid_at` = `datetime.fromtimestamp(CLOCK(), UTC)` for paid), record event → `200 {"status": "processed"}` |

The event record and the order change must be committed **together**.

## 3. `client.py` — `PaymentClient(api_key, transport, sleep=time.sleep, max_attempts=3, base_delay=0.5)`
`create_charge(order_reference, amount) -> dict`
- `amount <= 0` → `ValueError` (no call)
- call `transport("POST", "https://api.bayarkita.test/v1/charges", json={"order_reference", "amount"}, headers={"Authorization": "Bearer <api_key>", "Idempotency-Key": "charge-<order_reference>"}, timeout=10)` → returns `(status, body)` or raises `TimeoutError` / `ConnectionError`
- `2xx` → return `body`
- `4xx` except `429` → raise `PaymentRejected(status, body)` immediately (no retry)
- `429`, `5xx`, `TimeoutError`, `ConnectionError` → retry; sleep `base_delay * 2 ** (attempt - 1)` **between** attempts; after `max_attempts` failures raise `ProviderUnavailable`
- every attempt uses the **same** idempotency key

```bash
cd exercises
uv run pytest m2/w5/08-webhooks
```
