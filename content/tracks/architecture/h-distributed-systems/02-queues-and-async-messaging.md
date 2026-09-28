---
title: "Queues & Async Messaging"
summary: How to stop making users wait for slow work — a message queue lets one service hand a job to another and reply instantly, with at-least-once delivery, idempotent consumers, and a dead-letter queue for jobs that keep failing.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 120
tags: [architecture, distributed-systems, queue, async, messaging, sqs]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why slow work should run **after** you reply to the user
- What a **message queue** is and the **producer/consumer** pattern
- How queues **decouple** services and absorb traffic spikes
- **At-least-once** delivery and why consumers must be **idempotent**
- **Dead-letter queues** for jobs that keep failing
- Where this fits RevoShop (Module 5 added Redis queues)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Queue** | A line of jobs waiting to be done | Antrean pekerjaan |
| **Producer** | Code that puts a job on the queue | Yang menaruh pekerjaan |
| **Consumer / worker** | Code that takes jobs off and does them | Yang mengerjakan |
| **Async** | Do it later, don't make the caller wait | Nanti, tak menunggu |
| **Decouple** | Let two parts work without waiting on each other | Melepas ketergantungan |
| **At-least-once** | A job may be delivered more than once | Bisa terkirim lebih dari sekali |
| **Idempotent** | Doing it twice has the same effect as once | Dua kali sama seperti sekali |
| **Dead-letter queue** | A side bin for jobs that keep failing | Tempat pekerjaan gagal terus |

## 🧠 The big idea

A queue is the **order rail at a busy warung**. The cashier (**producer**) clips your order to the rail and immediately serves the next customer — they don't stand and cook. The cooks (**consumers**) pull tickets off the rail and cook at their own pace. The rail lets the front and the kitchen work **without waiting on each other**, and it holds the line steady during a lunch rush.

## ❓ Why it matters

Some work is slow: sending an email, resizing an image, calling an AI model, charging a card. If your web request *does* that work before replying, the user stares at a spinner for seconds, and a spike of orders can topple the server.

A queue fixes both: the web request drops a job on the queue and replies **instantly** ("we're processing your order"); workers do the slow part in the background. The site stays fast, and a traffic spike just makes the queue longer, not the server fall over.

## 📖 Step by step

### 1. Producer and consumer

Two roles, connected by a queue:

```
  web request (PRODUCER)  ──enqueue──▶  [ QUEUE ]  ──dequeue──▶  worker (CONSUMER)
      replies instantly                                          does the slow job
```

The producer adds a **message** (a small job description, e.g. `{"type": "send_receipt", "order_id": 42}`) and moves on. A separate worker process pulls messages and does the work.

### 2. Decoupling and absorbing spikes

Because they're connected only by the queue, producer and consumer **decouple**:

- The email service can be slow or briefly down — orders still get accepted; their receipt jobs just wait.
- A rush of 10,000 orders doesn't crash anything; the queue grows and workers catch up. (You can also add more workers.)

This is the main reason large systems lean on queues.

### 3. At-least-once delivery

Real queues (SQS, RabbitMQ, Redis-based) promise **at-least-once** delivery, not exactly-once. If a worker crashes after doing the work but before confirming (**ack**), the queue assumes it wasn't done and **redelivers** the message. So the same job can run twice.

```
worker takes "send_receipt #42" → sends email → CRASHES before ack
queue redelivers "send_receipt #42" → a second worker sends it again → duplicate email
```

### 4. So consumers must be idempotent

The fix (same idea as idempotent APIs): make the worker safe to run twice. Record which jobs you've already handled and skip duplicates.

```python
def handle(message, processed):
    if message["id"] in processed:      # already done this exact job
        return "skipped"
    do_the_work(message)
    processed.add(message["id"])        # mark done (in a shared store like Redis/DB)
    return "processed"
```

Now a redelivered message is detected and skipped, so "at-least-once" becomes "effectively once".

### 5. Dead-letter queues

Some jobs fail every time — bad data, a permanently missing record. Retrying forever clogs the queue. After a few failed attempts, move the message to a **dead-letter queue** (a side bin) so the main queue keeps flowing and a human can inspect the failures later.

```
attempt 1 ❌ → retry
attempt 2 ❌ → retry
attempt 3 ❌ → move to DEAD-LETTER QUEUE (stop retrying; alert someone)
```

### When to use a queue

| Situation | Queue? |
|---|---|
| Slow side work (email, image resize, AI call, report) | ✅ yes — do it async |
| Smoothing a traffic spike | ✅ yes — the queue buffers |
| The user must see the result on this very request | 🚫 no — do it inline |
| A simple, fast CRUD write | 🚫 no — a queue adds needless complexity |

- ✅ Queue slow, retryable, "can finish a moment later" work.
- ✅ Make every consumer idempotent and add a dead-letter queue.
- 🚫 Don't queue work whose result the caller needs *right now*.

## ⚠️ Common mistakes

- A non-idempotent consumer, so at-least-once delivery causes duplicate emails/charges.
- No dead-letter queue, so one poison message is retried forever and blocks others.
- Putting work the user needs immediately on a queue, so they never see the result on that request.
- Losing messages by acking *before* the work succeeds (ack only after success).
- Assuming strict ordering; most queues don't guarantee it — design so order doesn't matter, or use an ordered queue.

:::revoshop
Module 5 added Redis-based queues to RevoShop. (1) Which checkout steps should be async — sending the receipt email, notifying the seller, generating an invoice PDF — versus which must be inline (reserving stock, taking payment)? (2) The Midtrans webhook and a receipt worker can both run twice; is RevoShop's handling idempotent (does a duplicate change balances or send two emails)? (3) If an invoice job fails because a record is missing, what should happen after a few retries?
:::

## 🏆 Best practices

- [ ] Move slow, retryable side work off the request path onto a queue; reply instantly.
- [ ] Make every consumer idempotent (dedupe by message id in a shared store).
- [ ] Ack a message only *after* the work has succeeded.
- [ ] Add a dead-letter queue with a max-attempts limit and alerting.
- [ ] Keep messages small (ids and pointers, not huge payloads).
- [ ] Don't rely on ordering unless the queue guarantees it; design for out-of-order.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain a message queue with the warung order-rail analogy. Then explain, in two sentences, why at-least-once delivery means your worker must be idempotent.

## 📐 Design it

CareerPilot's "apply to 20 jobs" button must feel instant, but each application triggers slow work: tailor a CV with an AI call, send a confirmation email, and update a dashboard count. Design the async flow: what the web request does versus what workers do, how you keep the AI/email steps safe under at-least-once delivery, and what happens when the AI call for one job fails repeatedly.

:::quiz
Show a possible design

**Web request (producer):** validate the 20 jobs, write 20 `application` rows with status `queued`, enqueue 20 messages like `{"id": "app_1001", "type": "process_application"}`, and reply instantly ("processing your applications"). No slow work inline.

**Workers (consumers):** each pulls a message and does the slow steps — AI CV tailoring, send email, bump the dashboard count — then acks.

**At-least-once safety:** each worker is idempotent, keyed by the application id: if `app_1001` is already `done`, skip. The email send and count update also dedupe on that id, so a redelivered message doesn't send two emails or double-count.

**Repeated failure:** retry the AI step a few times (with backoff — next lesson); after max attempts, move `app_1001` to a **dead-letter queue**, mark the row `failed`, and alert. The other 19 keep flowing.

**Rule shown:** reply instantly, do slow work in idempotent workers, and dead-letter the jobs that won't succeed so one bad job doesn't block the rest.
:::

### 📝 Self-review checklist

- [ ] Only slow/retryable work is queued; the user gets an instant reply
- [ ] Consumers are idempotent, keyed by a stable id
- [ ] Ack happens after success; failures retry then dead-letter
- [ ] One failing job doesn't block the others

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/02-queue-consumer" ai="no-ai" title="A FIFO queue, an idempotent consumer, and a dead-letter queue"}
Implement a small FIFO queue, an idempotent consumer that skips messages it already processed (so at-least-once delivery doesn't double-charge), and a retry-with-dead-letter runner that retries a failing handler up to a limit before dead-lettering it. The tests replay a duplicate message and a permanently failing one.
:::

:::hints
- `Queue`: a list with `enqueue(msg)` appending and `dequeue()` popping from the front (`pop(0)`), returning `None` when empty.
- `consume_idempotently(processed, handler, message)`: if `message["id"]` is in `processed`, return `"duplicate"` without calling handler; else call handler, add the id, return `"processed"`.
- `process_with_retries(handler, message, max_attempts)`: call handler in a loop; a handler that raises means "failed". Return `("done", attempts)` on success or `("dead-letter", attempts)` if all attempts fail.
:::

## ✅ Quick check

:::quiz
Why does putting slow work on a queue keep your site fast during a traffic spike?

The web request just drops a small message and replies instantly, so users never wait for the slow work. A spike only makes the queue longer; workers drain it at their own pace (and you can add more), instead of the request path overloading and crashing.
:::

:::quiz
Queues deliver at-least-once. What does that force you to build into every consumer, and why?

Idempotency: because the same message can be delivered more than once (e.g. a worker crashes before acking), the consumer must detect a job it already handled and skip it — otherwise you get duplicate emails, charges, or counts.
:::

## 📚 Keep learning

- [AWS SQS: how queues work](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [AWS: dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Enterprise Integration Patterns: message queues](https://www.enterpriseintegrationpatterns.com/patterns/messaging/Message.html)
