---
title: "Pagination, Versioning & Idempotency"
summary: Three habits that keep an API safe as it grows — paginating big lists (offset vs cursor), versioning so you don't break old clients, and idempotency keys so a retried payment charges once, not twice.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: recommended }
durationMinutes: 130
tags: [architecture, api, pagination, versioning, idempotency, rest]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why returning a whole list is dangerous, and how to **paginate** it
- **Offset** vs **cursor** pagination, and when each fits
- How to **version** an API so old apps keep working
- **Idempotency**: making a repeated request safe (charge once, not twice)
- How these show up in a real checkout flow like RevoShop's

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Pagination** | Sending a big list in small pages | Membagi daftar jadi halaman |
| **Offset** | "Skip N rows, then give me the next page" | Lewati N baris |
| **Cursor** | A pointer to "continue after this item" | Penunjuk lanjut setelah item ini |
| **Versioning** | Keeping old and new API behavior side by side | Menjaga versi lama dan baru |
| **Breaking change** | A change that makes old clients fail | Perubahan yang merusak klien lama |
| **Idempotent** | Doing it again has the same effect as once | Diulang, hasilnya sama seperti sekali |
| **Idempotency key** | A client-sent id so the server ignores duplicates | Kunci agar duplikat diabaikan |

## 🧠 The big idea

- **Pagination** is a **book, not a scroll**: you read page by page, not one endless strip. Nobody hands you 2 million rows at once.
- **Versioning** is **keeping the old road open while you build the new one**: cars already on the old road don't crash just because you opened a better route.
- **Idempotency** is a **"already paid" stamp on a receipt**: if the waiter comes back with the same bill, the stamp says "this one's done — don't charge again".

## ❓ Why it matters

These three are what separates a toy API from a production one:

- No pagination → one request tries to return everything, and the server or phone runs out of memory.
- No versioning → the day you change a field, every old mobile app in the wild breaks.
- No idempotency → a shaky connection makes the client retry a "pay" request, and the customer is charged twice.

They are cheap to add early and painful to bolt on after real users arrive.

## 📖 Step by step

### 1. Pagination: never return the whole list

Return a **page** and tell the client how to get the next one.

**Offset pagination** — "skip N, take M":

```
GET /orders?limit=20&offset=40      → rows 41–60
```

Simple and lets you jump to any page. But on a big table, `offset=1000000` still makes the database count past a million rows (slow), and if new rows are inserted while you page, items can shift and you see duplicates or gaps.

**Cursor pagination** — "give me the next 20 after this item":

```
GET /orders?limit=20&after=order_1042    → the 20 orders after id 1042
```

The server uses the cursor with an indexed column (`WHERE id > 1042 ORDER BY id LIMIT 20`), which stays fast no matter how deep you go, and is stable when rows are added. The trade-off: you can't jump straight to "page 500", only go next/previous.

| | Offset | Cursor |
|---|---|---|
| Jump to any page | ✅ | ❌ (next/prev only) |
| Fast on deep pages | ❌ slows down | ✅ stays fast |
| Stable when data changes | ❌ can shift | ✅ stable |
| Best for | small/admin tables | infinite scroll, big feeds |

### 2. Versioning: change without breaking old clients

A **breaking change** is anything that makes existing clients fail: removing a field, renaming one, changing a type, or making an optional field required. A mobile app in someone's pocket can't be updated instantly, so you keep the old shape working.

Common approaches:

```
/v1/orders   and   /v2/orders          # version in the URL (most visible)
Accept: application/vnd.api+json; version=2   # version in a header
```

Rules of thumb: **add** fields freely (non-breaking); **never remove or repurpose** a field in the same version; introduce breaking changes only in a new version, and give old clients time to move.

### 3. Idempotency: make retries safe

The network is unreliable. A client sends "create payment", the response is lost, so the client **retries** — but the payment may already have gone through. Without protection, that's a double charge.

Fix: the client sends an **idempotency key** (a unique id it generates for that action):

```
POST /payments
Idempotency-Key: 7f3a-...-9c2
```

The server logic:

```python
def create_payment(key, amount):
    if key in seen:            # already processed this exact request
        return seen[key]       # return the SAME result, don't charge again
    result = charge(amount)
    seen[key] = result
    return result
```

Now retrying with the same key returns the first result instead of charging twice — the request is **idempotent**. Note: `GET`, `PUT`, and `DELETE` are naturally idempotent; `POST` (create) is the dangerous one that needs a key.

### Choosing your approach

| Situation | Do this |
|---|---|
| A list that can grow unbounded | Always paginate |
| Admin table, jump to page N | Offset pagination |
| Infinite scroll / huge feed | Cursor pagination |
| A public/mobile API you'll evolve | Version from day one (even `/v1`) |
| Any "create payment / place order" | Require an idempotency key |

- ✅ Paginate every list endpoint from the start.
- ✅ Ship `/v1` on day one so `/v2` has somewhere to go.
- ✅ Make money-moving and create operations idempotent.
- 🚫 Don't return unbounded lists "because it's small now".

## ⚠️ Common mistakes

- An endpoint that returns all rows, fine in testing, that falls over with real data.
- Deep offset pagination that gets slower every page on a big table.
- Removing or renaming a field without a new version, breaking old apps overnight.
- A retried `POST /payments` with no idempotency key → double charge.
- Reusing the same idempotency key for genuinely different actions (hides real requests).

:::revoshop
Look at RevoShop's checkout and list endpoints. (1) Does the orders/products list paginate, or could it return everything? Would offset or cursor fit the "my orders" page? (2) The Midtrans payment webhook can be delivered more than once — is RevoShop's handling **idempotent** (does processing the same payment twice change stock/balance twice)? (3) If you had to change an order response field, how would you do it without breaking a hypothetical old mobile client?
:::

## 🏆 Best practices

- [ ] Paginate every list; pick offset for admin/jump-to-page, cursor for big/growing feeds.
- [ ] Return pagination metadata (next cursor or total) so clients know how to continue.
- [ ] Version your API; only add fields within a version, never remove/rename.
- [ ] Require idempotency keys on create/payment endpoints; store and return the first result.
- [ ] Make webhook handlers idempotent — providers retry deliveries.
- [ ] Document deprecation timelines so clients have time to migrate.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain idempotency to a non-programmer with the "already paid" stamp analogy: why a shop that stamps the receipt won't charge you twice if the card machine hiccups and the cashier retries.

## 📐 Design it

CareerPilot lets users bulk-import saved jobs (could be thousands) and later "apply", which costs a paid credit. Design: (a) how the imported-jobs list is paginated and why; (b) how you'd version the API when you later add a required field to the apply request; (c) how you make "apply" safe against a double-click or a network retry so the user is never charged two credits.

:::quiz
Show a possible design

- **(a) Pagination**: the imported-jobs list can be huge and is scrolled, so use **cursor** pagination (`after=<job_id>`, indexed by `created_at, id`) — fast at any depth and stable while new imports arrive. Offset would slow down and could duplicate rows as imports are added.
- **(b) Versioning**: adding a *required* field is a breaking change. Ship it as `/v2/apply` (or a version header), keep `/v1/apply` working with a sensible default for the new field, announce a deprecation date, and remove `/v1` only after clients move.
- **(c) Idempotency**: the client generates one `Idempotency-Key` per apply action (per button press). The server stores `key → result`; a retry or double-click with the same key returns the first result and spends exactly one credit. The credit deduction and the "applied" record happen in one transaction.

**Rule shown:** paginate by access pattern, evolve behind versions, and protect credit/payment actions with idempotency keys.
:::

### 📝 Self-review checklist

- [ ] List pagination chosen by access pattern (offset vs cursor) with a reason
- [ ] Breaking change handled with a version and a migration path
- [ ] Create/credit action protected by an idempotency key + transaction
- [ ] Retries and double-clicks explicitly considered

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/05-pagination-idempotency" ai="no-ai" title="Pagination and idempotency keys"}
Implement offset pagination, cursor pagination (returning the items plus the next cursor), and an idempotent "create payment" that charges once even when called repeatedly with the same key. The tests prove cursor paging is stable when a row is inserted, and that a retried payment key returns the first result without charging again.
:::

:::hints
- `offset_page(items, offset, limit)` → `items[offset:offset+limit]`.
- `cursor_page(items, after_id, limit)`: find the index after the item whose id == after_id (or start at 0 if `after_id is None`); return `(page, next_cursor)` where next_cursor is the last item's id or `None` at the end.
- `create_payment(store, key, amount)`: if key in store return the stored result; else create `{"id": ..., "amount": amount, "charged": True}`, store it under key, return it.
:::

## ✅ Quick check

:::quiz
Why does cursor pagination stay fast on deep pages when offset pagination slows down?

Offset makes the database skip past all earlier rows (e.g. count a million rows to reach `offset=1000000`), which gets slower the deeper you go. A cursor uses an indexed `WHERE id > last` lookup, so it jumps straight to the next page regardless of depth.
:::

:::quiz
A payment request is retried after a lost response. How does an idempotency key prevent a double charge?

The client sends the same key on the retry; the server sees the key was already processed and returns the stored first result instead of charging again, so the effect is the same as calling once.
:::

## 📚 Keep learning

- [Stripe: idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [Slack: pagination (cursor-based)](https://api.slack.com/docs/pagination)
- [Google: API design — versioning](https://cloud.google.com/apis/design/versioning)
