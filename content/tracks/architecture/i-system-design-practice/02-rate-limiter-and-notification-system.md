---
title: "Rate Limiter & Notification System"
summary: Two classic design questions worked end to end — a distributed rate limiter (fixed vs sliding window, where the counter lives) and a notification system that fans one event out to email, push, and SMS with preferences and no duplicates.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 140
tags: [architecture, system-design, rate-limiter, notifications, fan-out, queue]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Designing a **distributed rate limiter** with the framework
- **Fixed window** vs **sliding window** counting, and the edge bug of fixed windows
- Where the counter lives so it works across many servers
- Designing a **notification system** that **fans out** one event to many channels
- Respecting **user preferences** and avoiding **duplicate** notifications
- Why notifications belong on queues with retries

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Rate limiter** | Caps how many requests are allowed in a time window | Pembatas jumlah request |
| **Fixed window** | Count resets on the clock (e.g. each minute) | Jendela reset per jam bulat |
| **Sliding window** | Count over the last N seconds from *now* | Jendela N detik terakhir |
| **Fan-out** | One event turns into many messages | Satu event jadi banyak pesan |
| **Channel** | A delivery route: email, push, SMS | Jalur kirim: email, push, SMS |
| **Preference** | Which channels a user wants | Pilihan saluran user |
| **Deduplicate** | Don't send the same thing twice | Jangan kirim dua kali |

## 🧠 The big idea

- A **rate limiter** is a **theme-park ride counter**: only so many riders per hour. The tricky part is how you count time — do you reset on the hour (fixed) or always look at the last 60 minutes (sliding)?
- A **notification system** is the **school's parent-announcement desk**: one announcement goes out, but each parent chose how they want it — SMS, email, or app — and nobody should get the same notice twice.

## ❓ Why it matters

These two show up constantly, in interviews and in real products. They also teach a key habit: a design isn't just "boxes", it's the **counting rule** (rate limiter) or the **routing + dedupe rules** (notifications) that decide correctness. Getting those rules right is what separates a design that works from one that double-sends or lets bursts through.

## 📖 Step by step

### Part A — Distributed rate limiter

**1. Requirements**: cap each user (or IP) to, say, 100 requests/minute; return `429` when exceeded; work across many server instances; be fast (checked on every request).

**2. Scale**: it runs on *every* request, so the check must be O(1)-ish and use a shared store.

**3. Fixed window**: count requests per clock minute.
```
key = "rl:user42:2026-09-29T10:15"   # per-minute bucket
INCR key ; if count > 100 → reject ; set expiry 60s
```
Simple, but it has an **edge bug**: 100 requests at 10:15:59 and 100 more at 10:16:00 = 200 requests in one real second, because the window reset on the clock boundary.

**4. Sliding window**: count over the last 60 seconds from *now*, not the clock minute. This smooths the edge — no burst at boundaries. It costs a little more (track timestamps or weight two adjacent windows).

**5. Where the counter lives**: in **Redis**, shared by all servers (a lone server's memory would give each instance its own separate limit). This is the same lesson as Stage F's rate limiting, now placed in a full design.

### Part B — Notification system

**1. Requirements**: when an event happens (e.g. "your order shipped"), notify the user on their chosen channels (email/push/SMS); respect **preferences**; never send **duplicates**; be reliable (retry failures); handle bursts.

**2. High-level flow**:
```
event  ──▶  Notification Service  ──▶  QUEUE  ──▶  channel workers
(order shipped)   │ fan-out per user prefs         email / push / SMS
                  └ dedupe by (user, event, channel)
```

**3. Fan-out**: one event becomes several messages — one per channel the user enabled. A user who wants email + push gets two messages; a user who muted this type gets none.

**4. Preferences**: check each user's settings before creating messages. Never spam a channel the user turned off (and honor "do not disturb"/unsubscribe — often a legal must).

**5. Dedupe**: the same event can be processed twice (at-least-once queues). Key each delivery by `(user_id, event_id, channel)` and skip if already sent — so a retry doesn't send two SMS.

**6. Reliability**: put deliveries on a **queue** with retries, backoff, and a dead-letter queue (Stage H). Email/SMS providers fail sometimes; the queue absorbs bursts and retries safely.

### Choosing the counting / delivery rules

| Decision | Pick |
|---|---|
| Simple cap, small edge bursts OK | Fixed window (easiest) |
| Smooth limiting, no boundary bursts | Sliding window |
| Counter for many servers | Always Redis (shared) |
| Reliable multi-channel sending | Queue + retries + dedupe |

- ✅ Store limiter counters in a shared store; expire keys automatically.
- ✅ Fan out per user preference; dedupe every delivery by a stable key.
- ✅ Send via queues with retries and a dead-letter queue.
- 🚫 Don't rate-limit in per-server memory; don't send without checking preferences.

## ⚠️ Common mistakes

- Fixed-window limiter allowing ~2× the limit across a boundary; use sliding window when that matters.
- Rate-limit state in one server's memory, so limits differ per instance.
- Sending notifications synchronously in the request, so a slow SMS provider stalls the app.
- No dedupe, so at-least-once processing double-sends emails.
- Ignoring preferences/unsubscribe — annoys users and can break laws.

:::revoshop
Design two RevoShop features. (1) **Login rate limit**: cap failed logins per account/IP — fixed or sliding window, and where does the counter live? What do you return on the 6th failed attempt? (2) **Order notifications**: "order shipped" should reach the buyer by their chosen channels; sketch the fan-out, how you honor preferences, and how you dedupe so a retried webhook doesn't email twice.
:::

## 🏆 Best practices

- [ ] Choose fixed vs sliding window based on whether boundary bursts matter; document it.
- [ ] Keep limiter counters in Redis with automatic expiry; return `429` + `Retry-After`.
- [ ] Fan out notifications per user preference; never send to disabled channels.
- [ ] Dedupe every delivery by `(user, event, channel)`.
- [ ] Deliver via queues with retries, backoff, and a dead-letter queue.
- [ ] Respect unsubscribe/do-not-disturb as a hard rule.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain fixed vs sliding window with the ride-counter analogy, including the boundary-burst bug. Then explain notification fan-out with the parent-announcement-desk analogy, including why dedupe matters.

## 📐 Design it

Design the notification system for CareerPilot: when an application's status changes to "interview scheduled", notify the user by their chosen channels (email, push, SMS), respecting preferences and do-not-disturb hours, never duplicating, and staying reliable if the SMS provider is briefly down. Cover fan-out, dedupe, and the delivery path.

:::quiz
Show a possible design

**Flow:** the app emits an `interview_scheduled {event_id, user_id, application_id}` event → Notification Service.

**Fan-out + preferences:** load the user's channel settings; create one message per **enabled** channel (say email + push, not SMS if they disabled it). Skip channels in a do-not-disturb window (or delay them until the window ends).

**Dedupe:** key each delivery `(user_id, event_id, channel)` in Redis/DB; if it exists, skip — so a re-emitted event or a queue redelivery doesn't send two emails.

**Delivery + reliability:** enqueue each message; channel workers call the email/push/SMS provider. On a transient provider error, retry with backoff (Stage H); after max attempts, dead-letter and alert. The SMS provider being down only delays SMS; email/push still go out.

**Rule shown:** fan out by preference, dedupe by a stable key, and deliver through queues with retries — so notifications are correct, respectful, and reliable.
:::

### 📝 Self-review checklist

- [ ] Counting rule (fixed/sliding) chosen with a reason; counter in a shared store
- [ ] Fan-out respects preferences and do-not-disturb
- [ ] Every delivery deduped by a stable key
- [ ] Delivery via queues with retries and dead-letter

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/02-notifications" ai="no-ai" title="Notification fan-out, preferences, and dedupe"}
Implement the core of a notification system: fan one event out to a user's enabled channels only, and deliver each message at most once (dedupe by user + event + channel). The tests check that disabled channels are skipped and that a redelivered event doesn't send duplicates.
:::

:::hints
- `fan_out(event, subscribers)`: for each subscriber, emit `{"user_id", "channel", "event_id"}` for every channel whose preference is True, in a fixed channel order (`email`, `push`, `sms`).
- `deliver_once(sent, message)`: build a key `(user_id, event_id, channel)`; if it's in `sent` return `"duplicate"`, else add it and return `"delivered"`.
- Keep both pure and deterministic — no real sending, no clocks.
:::

## ✅ Quick check

:::quiz
What is the edge bug of a fixed-window rate limiter, and how does a sliding window fix it?

A fixed window resets on the clock, so a user can send the full limit just before the boundary and again just after — nearly double the limit in a moment. A sliding window counts over the last N seconds from *now*, so there's no reset boundary to exploit and the rate stays smooth.
:::

:::quiz
Why must a notification system deduplicate deliveries, and what key works?

Because events and queue messages can be processed more than once (at-least-once), and without dedupe the user gets the same email/SMS twice. Keying each delivery by `(user_id, event_id, channel)` and skipping ones already sent makes delivery effectively once.
:::

## 📚 Keep learning

- [Cloudflare: rate limiting best practices](https://developers.cloudflare.com/waf/rate-limiting-rules/)
- [System Design: notification service](https://systemdesign.one/notification-service/)
- [Redis: rate limiting patterns](https://redis.io/glossary/rate-limiting/)
