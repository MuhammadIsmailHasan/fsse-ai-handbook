# Architecture · I · Notification Fan-Out & Dedupe

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build the core of a notification system.

| Function | Does |
|---|---|
| `fan_out(event, subscribers)` | One event → one message per **enabled** channel (`email`, `push`, `sms`) |
| `deliver_once(sent, message)` | Deliver at most once; dedupe by `(user, event, channel)` |

The tests prove disabled channels are skipped (and fully opted-out users get nothing), and that a redelivered event — normal with at-least-once queues — produces no duplicate sends.

```bash
cd exercises
uv run pytest architecture/i-system-design-practice/02-notifications
```
