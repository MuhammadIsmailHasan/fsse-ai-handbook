---
title: "Service Boundaries & Data Ownership"
summary: Each service owns its own data and is the only one allowed to touch those tables; others ask through its API. This one rule makes services truly independent — breaking it turns your microservices back into a monolith.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 90
tags: [microservices, data-ownership, boundaries, architecture]
lastReviewed: 2026-09
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What it means for a service to **own** its data
- Why the rule is: **only the owner touches the table**; everyone else asks the API
- What a **shared database** does to your services (it glues them back together)
- How services get the data they need without reaching into each other's tables
- How to spot a broken boundary before it hurts

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Data ownership** | One service is the only one allowed to read/write a set of tables | Kepemilikan data |
| **Boundary** | The edge of what a service owns and controls | Batas milik layanan |
| **Shared database** | Two or more services using the same tables directly | Database dipakai bersama |
| **API** | The front door a service offers others to ask it things | Pintu resmi layanan |
| **Source of truth** | The one place that holds the real, correct value | Sumber kebenaran |
| **Coupling** | How tightly two parts depend on each other | Saling bergantung |

## 🧠 The big idea

Think of each service as a **market stall with its own cash register and stock book**. The rule of the market is simple: **only the stall owner opens their own register.** If the sate stall wants to know the price of an es teh, it *asks* the drinks stall — it never walks behind the counter and opens the drinks stall's drawer.

If everyone could open everyone's register, you wouldn't really have separate stalls. You'd have one big shared drawer that several people reach into — and the moment one person rearranges it, everyone else's hand grabs the wrong thing.

That shared drawer is a **shared database**, and it is the single most common way "microservices" quietly turn back into a tangled monolith.

## ❓ Why it matters

The whole point of splitting into services is that each one can change on its own — its own deploy, its own schema, its own pace. **Data ownership is what makes that true.** If the Orders service is the only thing that touches the `orders` tables, then it can rename a column, add an index, or change how orders are stored, and nobody else even notices.

But the moment a second service reads or writes those same tables directly:

- Orders can no longer change its own tables safely — a rename now breaks the other service too.
- To deploy a schema change, **both** teams must coordinate and deploy together. That's exactly the pain microservices were supposed to remove.
- A bug in the other service can corrupt Orders' data, and Orders gets blamed for data it didn't write.
- There is no longer one clear **source of truth** — two services both "own" the value, and they drift apart.

So a shared database gives you all the costs of microservices (network, many apps, complexity) with **none** of the independence. You'd genuinely be better off with a single clean monolith. The boundary rule — *own your data, ask for everyone else's* — is what buys the independence back.

## 📖 Step by step

### 1. One owner per table

Every table has exactly **one** owning service. That service is the only code that runs `SELECT`, `INSERT`, `UPDATE` or `DELETE` on it.

| Tables | Owner |
|---|---|
| `products`, `product_images` | Catalog service |
| `orders`, `order_items` | Orders service |
| `payments`, `refunds` | Payments service |

If you can't say who owns a table in one word, that's a sign the boundary isn't clear yet — which is a reason to keep those parts together (monolith first).

### 2. How others get the data: ask, don't reach

The Orders service needs a product's name and price. It does **not** query the `products` table. Instead it asks the Catalog service through its API:

```python
# Inside the Orders service — it has NO access to the products table.
product = catalog_client.get_product(product_id)   # an HTTP call to Catalog
line_total = product.price * quantity
```

Catalog stays in charge of what a "product" is and how it's stored. Orders just receives the answer.

### 3. When you can't call every time: keep a copy

Asking over the network every time can be slow, and it fails if the other service is down. So services often **keep a small copy** of the bits they need — and remember that the copy is *not* the source of truth.

For example, when an order is placed, Orders can store the product's **name and price at that moment** right inside the `order_items` row:

```python
# Store the price AS IT WAS when the order was placed.
order_item = OrderItem(
    product_id=product.id,
    product_name=product.name,   # a snapshot, owned by Orders now
    unit_price=product.price,    # the price the customer actually paid
    quantity=quantity,
)
```

This is not breaking the rule — it's the *right* thing. An order must remember the price the customer paid even if Catalog changes the price tomorrow. The snapshot belongs to the order. Catalog is still the source of truth for the *current* price.

### 4. Staying up to date

If a service needs to react when another's data changes (Catalog lowers a price, and Search must re-index), the owner **publishes an event** — "product 42 changed" — and interested services update their own copies. You'll see this async pattern in the next lesson. The key idea stays the same: **the owner announces; others keep their own copy.** Nobody reaches into the owner's tables.

### Choosing your setup

- ✅ One clear owner per table; everyone else uses the owner's API.
- ✅ Snapshots of data that must not change later (the price paid, the address shipped to).
- 🚫 Two services writing the same table — that's one service in disguise; keep them together.
- 🚫 A "shared" database "just for reporting" that slowly grows into shared writes.

## ⚠️ Common mistakes

- A **shared database** where several services read and write the same tables — the classic trap.
- One service reaching into another's tables "just to read" — a read today becomes a write tomorrow, and either way the owner can no longer change its schema freely.
- Splitting the code into services but leaving **one big database** behind them. The database is where the coupling lives, so that's a monolith with extra network hops.
- Treating a local copy as the source of truth and letting two services both "own" the same value.

## 🏆 Best practices

- [ ] Give every table exactly **one** owning service.
- [ ] Let only the owner read and write its tables; everyone else uses the API.
- [ ] Store **snapshots** of values that must stay fixed (price paid, address used).
- [ ] Keep local copies for speed, but remember the owner is the source of truth.
- [ ] If two parts must share a database, treat that as a sign to keep them as **one** service.

:::revoshop
1. **List the owners.** Group RevoShop's tables by who would own them if you split: catalog (`products`…), orders (`orders`, `order_items`…), payments (Midtrans-related), users/auth. Is every table easy to place under one owner?
2. **Find the tangles.** Are there tables that several parts read *and* write (for example, does order code write to product stock)? Those are the hard boundaries — the coupling that would make a split painful.
3. **Snapshot check.** When a RevoShop order is placed, does an order line store the price at purchase time, or does it read the current product price later? Which is correct, and why?
4. **The honest call.** Because RevoShop shares one database today, splitting a service would mean first *un-sharing* those tables. Is that work worth it now? (Naming the work is the point — you don't have to do it.)
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

A teammate wants to split RevoShop into an Orders service and a Catalog service but "keep the same database so it's easier". Using the market-stall analogy, explain why that shared database throws away the whole benefit of splitting.

## 📐 Design it

Design the Orders ↔ Catalog boundary. Say which tables each owns, exactly what Orders needs from Catalog, whether it asks each time or keeps a snapshot, and what happens to an old order's price when Catalog changes the price tomorrow.

:::quiz
Show a possible answer

Catalog owns `products` and `product_images`; Orders owns `orders` and `order_items`. When placing an order, Orders asks Catalog for the current name and price (an API call), then **stores a snapshot** of `product_name` and `unit_price` on the order line. Later, if Catalog raises the price, old orders are unaffected — they keep the price the customer actually paid, because that value now belongs to the order. Catalog remains the source of truth for the *current* price shown on the product page.
:::

### 📝 Self-review checklist

- [ ] Every table has exactly one owner
- [ ] No service reads or writes another's tables directly
- [ ] Values that must not change later are stored as snapshots

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w5/02-data-ownership" ai="no-ai" title="Find broken data boundaries"}
Given a set of services and the tables each one owns and writes to, write `find_ownership_violations(services)` that reports every case where a service writes to a table another service owns — the shared-database trap that turns microservices back into a monolith.
:::

:::hints
- First build a map from `table -> owner name` by walking every service's `owns` set.
- Then, for each service, look at every table it `writes` that is owned by a *different* service.
- Build each message with an f-string and `sorted(...)` the final list so the output is stable.
:::

## ✅ Quick check

:::quiz
Why does a shared database cancel out most of the benefit of splitting into services?

Independence comes from each service controlling its own data. If two services touch the same tables, neither can change its schema without breaking the other, so they must deploy together and coordinate constantly — exactly the coupling microservices were meant to remove. You pay the cost of many apps and get none of the freedom.
:::

:::quiz
An order line stores `unit_price` at the time of purchase, even though the Catalog service owns product prices. Is that a boundary violation?

No — it's correct. The price the customer paid is a fact that belongs to the order and must never change, so Orders stores its own snapshot. Catalog is still the source of truth for the *current* price. Orders isn't reading Catalog's tables; it copied a value at order time.
:::

## 📚 Keep learning

- [Microservices.io: Database per service](https://microservices.io/patterns/data/database-per-service.html)
- [Martin Fowler: BoundedContext](https://martinfowler.com/bliki/BoundedContext.html)
- [microservices.io: Shared database anti-pattern](https://microservices.io/patterns/data/shared-database.html)
