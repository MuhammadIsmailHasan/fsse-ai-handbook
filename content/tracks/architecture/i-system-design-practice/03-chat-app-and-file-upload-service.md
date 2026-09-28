---
title: "Chat App & File Upload Service"
summary: Two more design classics — a real-time chat (WebSockets vs polling, storing and ordering messages, presence) and a file upload service that sends big files straight to object storage with presigned URLs and resumable chunks.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: recommended }
durationMinutes: 140
tags: [architecture, system-design, chat, websockets, file-upload, s3]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Real-time delivery: **polling** vs **WebSockets**, and when each fits
- Storing and **ordering** chat messages per conversation
- **Presence** (who's online) and fan-out to conversation members
- Uploading big files without choking your server: **presigned URLs** to object storage
- **Chunked / resumable** uploads for large or flaky connections
- Serving files fast with a **CDN**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Polling** | The client keeps asking "anything new?" | Klien terus bertanya |
| **WebSocket** | A kept-open two-way connection for live push | Koneksi hidup dua arah |
| **Presence** | Whether a user is online right now | Status online user |
| **Object storage** | A store for files/blobs (like S3) | Penyimpan berkas (S3) |
| **Presigned URL** | A temporary link letting a client upload straight to storage | Tautan unggah sementara |
| **Chunk** | A piece of a big file uploaded separately | Potongan berkas |
| **Resumable** | Continue an upload after a drop | Bisa dilanjutkan |
| **CDN** | Edge servers that serve files close to users | Server tepi dekat user |

## 🧠 The big idea

- **Chat** is the difference between **checking your mailbox every minute** (polling) and **having a phone line open** (WebSocket) — the open line delivers the moment something is said, instead of you asking again and again.
- **File upload** is like **shipping a wardrobe**: you don't carry it through the front office (your app server). You give the courier a **direct address to the warehouse** (a presigned URL to object storage), and for a huge item you ship it in **boxes** (chunks) that can be re-sent if one is lost.

## ❓ Why it matters

Both look simple ("just send messages", "just upload a file") and both punish naive designs. Polling for chat wastes huge resources and still feels laggy. Uploading big files *through* your app server ties up memory and bandwidth and falls over on a dropped connection. The right patterns — WebSockets and direct-to-storage chunked uploads — are what real products use, and they come up constantly in interviews.

## 📖 Step by step

### Part A — Real-time chat

**1. Requirements**: send/receive messages in near real-time; 1:1 and group chats; message history; ordering; ideally presence and delivery/read receipts.

**2. Delivery: polling vs WebSocket**

| | Polling | WebSocket |
|---|---|---|
| How | Client asks every few seconds | Server pushes over an open connection |
| Latency | Laggy (up to the poll interval) | Instant |
| Server load | Wasteful (many empty checks) | Efficient for live updates |
| Best for | Rare updates | Chat, live feeds, presence |

Chat wants **WebSockets** (or a similar push transport): the server pushes a new message to connected recipients immediately.

**3. Storing and ordering messages**: store messages per **conversation**. Order them with a **per-conversation sequence number** or a reliable timestamp — not the client's clock, which can be wrong. Reads use cursor pagination (Stage F) to load history.

```
messages( id, conversation_id, sender_id, seq BIGINT, body, created_at )
-- ordered within a conversation by seq
```

**4. Fan-out and presence**: when a message arrives, deliver it to the conversation's members who are connected (via their WebSocket), and store it for those who are offline to fetch later. **Presence** (online/offline) is kept in a fast store (Redis) and updated as connections open/close.

**5. Scale note**: with many servers, users on *different* servers must still reach each other. A shared pub/sub (e.g. Redis pub/sub) routes a message to whichever server holds the recipient's connection.

### Part B — File upload service

**1. Requirements**: upload files (some large) reliably; store them durably; serve them fast; handle flaky mobile connections.

**2. Don't upload through your app server.** Piping a 2 GB video through your web process eats memory and bandwidth. Instead, hand the client a **presigned URL** — a temporary, permission-scoped link that lets it upload **directly to object storage** (S3). Your server only issues the link and records metadata.

```
1. client → app: "I want to upload video.mp4"
2. app → client: presigned URL (valid 15 min, write-only, this key)
3. client → object storage: PUT the file directly
4. client → app: "done" ; app saves metadata (owner, key, size)
```

**3. Chunked / resumable uploads**: for big files or shaky connections, split the file into **chunks** and upload them separately. If one chunk fails, re-send just that chunk — no restarting the whole upload. When all chunks are in, the upload is **complete** and can be assembled.

**4. Metadata vs blob**: keep the *file bytes* in object storage; keep *metadata* (owner, filename, size, content-type, key) in your database. This mirrors the pastebin lesson: DB for small structured data, object storage for big blobs.

**5. Serving fast**: put a **CDN** in front of object storage so downloads come from an edge near the user. Use short-lived presigned URLs (or signed CDN URLs) for private files.

### Choosing the approach

| Need | Do this |
|---|---|
| Live messages / presence | WebSockets + Redis pub/sub across servers |
| Rare updates only | Polling is fine and simpler |
| Any large file upload | Presigned URL direct to object storage |
| Huge / flaky uploads | Chunked, resumable upload |
| Fast global downloads | CDN in front of storage |

- ✅ Order chat by a server-assigned sequence, not the client clock.
- ✅ Upload big files direct-to-storage with presigned URLs; store only metadata in the DB.
- ✅ Chunk large/flaky uploads so a failure re-sends one chunk, not everything.
- 🚫 Don't poll for real-time chat, and don't stream big files through your app server.

## ⚠️ Common mistakes

- Polling every second for chat — heavy load and still laggy; use WebSockets.
- Ordering messages by the client's clock, so messages appear out of order.
- Uploading large files through the app server, exhausting memory and failing on drops.
- Storing file bytes in the database instead of object storage.
- No resumability, so a dropped connection restarts a huge upload from zero.

:::revoshop
Two possible RevoShop features. (1) **Seller–buyer chat**: would you poll or use WebSockets, how would you order and store messages, and where does presence live? (2) **Product image upload**: sketch a presigned-URL flow so images go straight to object storage (not through Flask), what metadata you'd store in PostgreSQL, and how a CDN would speed up serving product images.
:::

## 🏆 Best practices

- [ ] Use WebSockets (or similar push) for real-time; reserve polling for rare updates.
- [ ] Assign a server-side sequence/timestamp for message ordering; paginate history with cursors.
- [ ] Keep presence and cross-server routing in a shared store / pub-sub.
- [ ] Upload large files direct to object storage via short-lived presigned URLs.
- [ ] Chunk large uploads for resumability; verify all chunks before marking complete.
- [ ] Store blobs in object storage and metadata in the DB; serve via a CDN.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain polling vs WebSockets with the mailbox vs open-phone-line analogy. Then explain presigned uploads with the ship-the-wardrobe-straight-to-the-warehouse analogy, including why chunks help on a flaky connection.

## 📐 Design it

Design file upload for CareerPilot: users upload a CV (small PDF) and, on some plans, a short intro **video** (up to 500 MB) from mobile. Design the upload path for both, how you handle the large flaky video upload, what you store where, and how you serve the files back quickly and privately.

:::quiz
Show a possible design

**CV (small PDF):** still use a **presigned URL** to object storage so bytes never pass through the app server. The app issues the URL, the client PUTs directly, then the app stores metadata (`user_id`, `key`, `size`, `content_type`) in PostgreSQL. A single PUT is fine at this size.

**Intro video (up to 500 MB, mobile):** use a **chunked, resumable** upload — split into, say, 5–10 MB chunks, each with its own presigned URL; re-send only failed chunks. Mark the upload complete only when every chunk is present, then assemble/finalize in object storage.

**Storage split:** blobs (PDF, video) in object storage; metadata in the DB. Never store the video bytes in PostgreSQL.

**Serving privately + fast:** serve through a **CDN** with **short-lived signed URLs** so only the owner (or authorized viewers) can fetch, and downloads come from an edge near the user.

**Rule shown:** direct-to-storage presigned uploads for everything, chunked/resumable for big flaky files, metadata in the DB, and a CDN with signed URLs for fast private serving.
:::

### 📝 Self-review checklist

- [ ] Uploads go direct to object storage (not through the app server)
- [ ] Large/flaky uploads are chunked and resumable
- [ ] Blobs in object storage, metadata in the DB
- [ ] Serving is fast (CDN) and access-controlled (signed URLs)

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/03-chunked-upload" ai="no-ai" title="Resumable chunked upload tracker"}
Implement the tracker behind a resumable upload: receive chunks by index (idempotently), report which chunks are still missing, tell when the upload is complete, and assemble the chunks in order once they're all present. The tests re-send a duplicate chunk and finish an upload out of order.
:::

:::hints
- Store received chunks in a dict `{index: data}`; `receive` returns `"stored"` or `"duplicate"` (already have that index).
- `missing()` = sorted list of indices in `range(total)` not yet received.
- `is_complete()` = we have all `total` indices. `assemble()` raises if incomplete, else returns data in index order (`0..total-1`).
:::

## ✅ Quick check

:::quiz
Why are WebSockets a better fit than polling for a chat app?

Polling makes the client ask repeatedly, wasting resources on mostly-empty checks and still lagging up to the poll interval. A WebSocket keeps a connection open so the server pushes each new message instantly — lower latency and far less wasted load for live updates.
:::

:::quiz
Why upload large files with a presigned URL to object storage instead of through your app server?

Because streaming a big file through the app server consumes its memory and bandwidth and fails badly on a dropped connection. A presigned URL lets the client upload directly to durable object storage; the server only issues the link and records metadata, and chunking makes the upload resumable.
:::

## 📚 Keep learning

- [MDN: WebSockets API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [AWS S3: presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- [AWS S3: multipart (chunked) upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
