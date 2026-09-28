---
title: "REST vs GraphQL vs gRPC"
summary: Three ways to shape an API — REST's simple resources, GraphQL's ask-for-exactly-what-you-need queries, and gRPC's fast service-to-service calls — with over-fetching shown by hand and a clear rule for which to pick.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: optional }
durationMinutes: 130
tags: [architecture, api, rest, graphql, grpc, over-fetching]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What REST, GraphQL, and gRPC each are, in plain terms
- **Over-fetching** and **under-fetching** — the problems GraphQL targets
- How a GraphQL query asks for exactly the fields it wants
- Where gRPC fits (fast internal service-to-service calls)
- A simple rule for choosing between the three

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **API** | The agreed way one program asks another for data | Cara program saling minta data |
| **REST** | An API built around resources at URLs (`/users/1`) | API berbasis URL sumber daya |
| **Endpoint** | One URL that does one job | Satu URL untuk satu tugas |
| **GraphQL** | One endpoint where the client asks for exact fields | Satu endpoint, minta field persis |
| **gRPC** | A fast binary way for servers to call each other | Cara cepat antar-server |
| **Over-fetching** | Getting more data than the screen needs | Mengambil lebih dari yang perlu |
| **Under-fetching** | One call isn't enough, so you make several | Satu panggilan kurang, jadi berkali-kali |
| **Schema (GraphQL)** | The typed catalog of what you can ask for | Katalog berjenis yang bisa diminta |

## 🧠 The big idea

Think of ordering food:

- **REST** is a **fixed-menu warung**: each dish (endpoint) is prepared one way. `/users/1` gives you the whole "user" dish, even the parts you won't eat.
- **GraphQL** is a **build-your-own bowl**: you tell the kitchen exactly which ingredients (fields) you want, and you get back exactly that — no more, no less, in one trip.
- **gRPC** is the **kitchen's internal intercom**: cooks talking to cooks, fast and terse, not meant for customers out front.

## ❓ Why it matters

Most of your career you will build and call APIs. Picking the wrong style makes the frontend slow (too many round trips) or wasteful (downloading fields nobody shows). Picking the right one — usually REST, sometimes GraphQL, gRPC for internal calls — keeps apps fast and simple. You also need to *read* all three, because real systems mix them.

## 📖 Step by step

### 1. REST: resources at URLs

REST models your data as **resources**, each at a URL, using HTTP verbs (you learned these in Module 2):

```
GET    /users/1          → one user
GET    /users/1/orders   → that user's orders
POST   /orders           → create an order
```

Simple, cacheable, and everyone understands it. It is the **default** for public web APIs.

The weakness: each **endpoint** returns a fixed shape. A screen showing just a user's name and avatar still downloads the whole user object — **over-fetching**. And showing a user *plus* their orders may need two calls — **under-fetching**.

### 2. GraphQL: ask for exactly what you need

GraphQL has **one endpoint**. The client sends a query describing the exact fields — including nested ones — and gets back that shape:

```graphql
query {
  user(id: 1) {
    name
    avatarUrl
    orders(last: 3) {
      total
    }
  }
}
```

The response mirrors the query — only `name`, `avatarUrl`, and the last 3 orders' totals. One trip, no over-fetching, no under-fetching. This shines when many different screens (web, mobile) need different slices of the same data.

The cost: a GraphQL server is more work to build and secure. A single query can ask for very expensive nested data, so you must add limits (depth, complexity). Simple HTTP caching by URL no longer applies, because everything is one endpoint.

### 3. gRPC: fast service-to-service calls

gRPC is built for **servers talking to servers** inside your system. It sends compact **binary** messages (defined in a `.proto` file) instead of text JSON, which is faster and smaller.

```proto
service Orders {
  rpc GetOrder (OrderRequest) returns (Order);
}
```

You would use gRPC between your own microservices (order service ↔ payment service), not usually for a browser or public clients. It trades human-readability and easy debugging for speed and a strict contract.

### 4. Over-fetching, felt

Imagine a user object with 15 fields, but a list screen only shows `name`:

| Style | What the screen gets |
|---|---|
| REST `/users` | all 15 fields per user (over-fetch) |
| GraphQL `{ users { name } }` | just `name` per user |

On a big list over a phone connection, that difference is real bytes and real seconds. (REST can add `?fields=name`, but then you are slowly reinventing GraphQL.)

### Choosing your API style

| Situation | Good choice |
|---|---|
| Public web API, simple resources, want caching | **REST** — start here |
| Many clients needing different field selections; complex nested data | **GraphQL** |
| Internal service-to-service calls where speed matters | **gRPC** |
| A small app with one frontend | **REST** — don't over-engineer |

- ✅ Default to REST; it is simplest, cacheable, and universally understood.
- ✅ Reach for GraphQL when varied clients genuinely suffer from over/under-fetching.
- ✅ Use gRPC for internal, high-throughput calls — not public browser APIs.
- 🚫 Don't adopt GraphQL "because it's modern" for one simple frontend.

## ⚠️ Common mistakes

- Choosing GraphQL for a single simple client, then maintaining a complex server for no benefit.
- Exposing gRPC directly to browsers (it needs a proxy; it's meant for internal calls).
- REST endpoints that return giant objects when screens need three fields.
- GraphQL with no depth/complexity limits, letting one query hammer the database.
- Forgetting REST's free HTTP caching that GraphQL gives up.

:::revoshop
RevoShop's API is REST (flask-smorest). (1) Find an endpoint that returns a big object where a screen shows only a few fields — is that over-fetching? (2) The product list page then fetches each product's reviews separately — is that under-fetching, and would one combined response help? (3) If RevoShop later split into services (catalog, orders, payments), where would gRPC calls between them make sense, while the browser still talks REST to the edge?
:::

## 🏆 Best practices

- [ ] Default to REST; adopt GraphQL or gRPC only for a problem they clearly solve.
- [ ] Design REST endpoints around the screens that use them to limit over/under-fetching.
- [ ] In GraphQL, enforce depth/complexity limits and paginate list fields.
- [ ] Keep gRPC for internal service-to-service traffic; put REST or GraphQL at the public edge.
- [ ] Version and document whichever style you choose; keep the contract stable.
- [ ] Measure payload size and round trips before switching styles for "performance".

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain REST vs GraphQL to a non-programmer with the fixed-menu-warung vs build-your-own-bowl analogy. Then say, in one sentence each, what over-fetching and under-fetching are.

## 📐 Design it

CareerPilot has three clients of the same data: a web dashboard (shows a lot per application), a mobile app (shows a tiny card: company + status), and a nightly export job (needs every field). Decide whether REST or GraphQL serves these three better, and why. Then say where gRPC might appear if CareerPilot's AI suggestion engine became its own internal service.

:::quiz
Show a possible design

**Public API for the three clients → GraphQL is a strong fit**, because the same data is viewed at very different detail levels: mobile asks `{ application { company status } }`, web asks for many fields, and the export asks for all — each in one round trip, no over/under-fetching. REST would need either fat responses (over-fetch for mobile) or many tailored endpoints.

**If the app is still small / one main client**, REST with a couple of well-shaped endpoints is simpler and cacheable — don't add GraphQL yet.

**gRPC**: between the main API service and the internal AI suggestion service (`GetSuggestions(profile) → suggestions`), where speed and a strict contract matter and no browser is involved. The browser still talks REST/GraphQL to the edge.

**Rule shown:** match the style to who calls it — varied external clients → GraphQL; internal service-to-service → gRPC; simple public resources → REST.
:::

### 📝 Self-review checklist

- [ ] Choice justified by client variety and data shape, not hype
- [ ] Over/under-fetching addressed for each client
- [ ] gRPC placed only on internal calls
- [ ] Caching and complexity trade-offs acknowledged

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/04-graphql-select" ai="no-ai" title="A tiny GraphQL-style field selector"}
Build the core idea behind GraphQL by hand: a `graphql_select` that returns only the requested fields of an object (including nested ones), and an `over_fetch_count` that shows how many extra fields a REST-style "return everything" response sends compared to a field-selected one. The tests prove the selector avoids over-fetching.
:::

:::hints
- Selection is a dict: `{"name": True, "orders": {"total": True}}` — a value of `True` means "include this leaf", a dict means "recurse".
- For a list field (like `orders`), apply the nested selection to each item.
- `over_fetch_count` = (fields in the full object) − (fields actually requested), counted as leaves.
:::

## ✅ Quick check

:::quiz
What problem does GraphQL mainly solve compared to REST?

Over-fetching and under-fetching: the client asks for exactly the fields it needs (including nested data) in one request, instead of downloading whole fixed objects or making several REST calls.
:::

:::quiz
Why is gRPC usually a bad fit for talking directly to a web browser?

gRPC uses compact binary messages meant for fast service-to-service calls and needs a special proxy to reach browsers; it gives up the human-readable, easily-cached, widely-supported HTTP/JSON that browsers and public clients expect.
:::

## 📚 Keep learning

- [MDN: REST & designing web APIs](https://developer.mozilla.org/en-US/docs/Glossary/REST)
- [GraphQL: learn / queries](https://graphql.org/learn/queries/)
- [gRPC: introduction](https://grpc.io/docs/what-is-grpc/introduction/)
