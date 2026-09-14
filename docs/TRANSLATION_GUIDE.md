# Translation Guide — Bahasa Indonesia

The handbook is bilingual. **English is the source of truth**; Indonesian translations
sit next to each lesson and fall back to English (with a "Belum diterjemahkan" badge)
when missing.

```
content/modules/m4/w1/01-html-structure-and-semantics.md     ← English
content/modules/m4/w1/01-html-structure-and-semantics.id.md  ← Bahasa Indonesia
content/course.id.json                                        ← module/week/track titles
src/i18n/messages.ts                                          ← app UI text
```

## Workflow

1. Copy the English lesson to `<name>.id.md`.
2. Replace the frontmatter with only:
   ```yaml
   ---
   title: 'Struktur & Semantik HTML'
   summary: Satu atau dua kalimat (maks. 300 karakter).
   sourceHash: 000000000000
   ---
   ```
   Roles, duration, tags, `sourceRef`… come from the English file automatically.
3. Translate the body.
4. `npm run i18n -- stamp content/.../<name>.id.md` — records which English version you translated.
5. `npm run content:check` — must pass. `npm run i18n` shows coverage.

When the English lesson changes later, `content:check` reports the translation as **stale**.
Update the Indonesian text, then stamp again.

## What must stay identical (checked automatically)

- Every directive, in order, with the same attributes: `::part{n}`, `:::exercise{path ai}`,
  `:::quiz`, `:::hints`, `::::placement{id}`, `:::revoshop`, `::ai-review{task}`…
  Labels (`::part[Pelajari Konsepnya]`, `:::tip[Judul]`) and `title="…"` **may** be translated.
- Code blocks: same count, same order, same language — and **code is not edited**
  (comments too). Only ` ```mermaid `, ` ```text ` and plain ` ``` ` blocks may be translated.
- Internal links: the same set of pages.

## Style

- **Register:** friendly and direct, like a senior colleague — use **kamu** (not _Anda_), _kita_ for "we".
- **Keep technical terms in English** when Indonesian developers use them in English at work:
  _component, props, state, hook, render, route, request/response, endpoint, deploy, build, commit,
  branch, pull request, test, bug, debug, framework, library, package, runtime, middleware, cache,
  query, schema, token, session, cookie, frontend/backend, responsive, layout, breakpoint, callback,
  promise, async/await, type, interface, generic, union, placeholder, form, input, event, handler._
  Inflect with a hyphen when needed: _di-render_, _di-deploy_, _me-review_, _nge-fetch_ → prefer _mengambil data (fetch)_.
- **Translate** general words: _pelajari, contoh, latihan, langkah, masalah, solusi, peringatan, tujuan,
  kesalahan umum, praktik terbaik_.
- Inline code, file names, commands, UI labels in code (`"Send"`) and API names stay unchanged.
- `:term[Middleware]{bahasa="…"}` — keep the term in English; the `bahasa` explanation is already Indonesian.
- Numbers and money: `Rp 14 juta`, decimals with a comma in prose (`1,5 jam`) but never inside code.
- Don't translate brand/product names: RevoShop, CareerPilot, Next.js, Tailwind CSS, Playwright.

## Standard section headings

| English                                                               | Bahasa Indonesia                                                    |
| --------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `::part[Learn the Concept]` / `[Explain & Design]` / `[Toy Exercise]` | `[Pelajari Konsepnya]` / `[Jelaskan & Rancang]` / `[Latihan Kecil]` |
| 🎯 What you'll learn                                                  | 🎯 Yang akan kamu pelajari                                          |
| 🧠 The big idea                                                       | 🧠 Ide besarnya                                                     |
| ❓ Why does this exist?                                               | ❓ Kenapa ini ada?                                                  |
| 💥 What happens if we DON'T?                                          | 💥 Apa yang terjadi kalau TIDAK?                                    |
| 📖 How it works, step by step                                         | 📖 Cara kerjanya, langkah demi langkah                              |
| 🏭 How it's used in industry                                          | 🏭 Cara dipakai di industri                                         |
| ✅ When to use it / 🚫 When NOT to use it                             | ✅ Kapan dipakai / 🚫 Kapan TIDAK dipakai                           |
| ⚖️ Trade-offs                                                         | ⚖️ Trade-off                                                        |
| ⚠️ Common mistakes                                                    | ⚠️ Kesalahan umum                                                   |
| 🏆 Best practices                                                     | 🏆 Praktik terbaik                                                  |
| 📖 Kamus (glossary)                                                   | 📖 Kamus (glosarium)                                                |
| ✅ Quick check                                                        | ✅ Cek cepat                                                        |
| 🗣️ Explain it                                                         | 🗣️ Jelaskan                                                         |
| 📐 Design it                                                          | 📐 Rancang                                                          |
| 📚 Keep learning                                                      | 📚 Lanjut belajar                                                   |
| 📣 End of Week N — share your progress                                | 📣 Akhir Minggu N — bagikan progresmu                               |
