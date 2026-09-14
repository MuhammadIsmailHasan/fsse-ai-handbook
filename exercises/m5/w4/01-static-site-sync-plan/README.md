# M5 · W4 · 01 — Deploy plan for a static frontend on S3 + CloudFront

> 🚫🤖 **No-AI** · ⏱️ ~90 min · no AWS account needed

`aws s3 sync` uploads files, but a *good* static deploy also sets the right **cache headers** and **content types**, deletes stale files **after** the new version is live, and invalidates only what must be invalidated. Write the planner in `sync_plan.py` (the part a deploy script runs before calling S3 and CloudFront).

## Inputs
- `local: dict[str, bytes]` — relative paths (`index.html`, `_next/static/chunks/app-3f9a.js`) → file contents
- `remote: dict[str, str]` — keys currently in the bucket → their ETag (for single-part uploads the ETag is the **MD5 hex** of the content)

## 1. `cache_control(path) -> str`
| Path | Header |
|---|---|
| under `_next/static/` or `assets/`, **or** a filename containing a content hash (`name.<8+ hex chars>.<ext>`, e.g. `app.3f9a1c2b.js`) | `public, max-age=31536000, immutable` |
| `*.html` and `sw.js` | `public, max-age=0, must-revalidate` |
| anything else (`robots.txt`, `favicon.ico`, `images/logo.png`) | `public, max-age=3600` |

## 2. `content_type(path) -> str`
Map extensions: `html`→`text/html; charset=utf-8`, `css`→`text/css; charset=utf-8`, `js`/`mjs`→`text/javascript; charset=utf-8`, `json`→`application/json`, `svg`→`image/svg+xml`, `png`, `jpg`/`jpeg`, `webp`, `avif`, `ico`→`image/x-icon`, `woff2`→`font/woff2`, `txt`→`text/plain; charset=utf-8`, `xml`→`application/xml`, `map`→`application/json`; unknown → `application/octet-stream`.

## 3. `plan(local, remote, *, delete=True) -> Plan`
`Plan(uploads, deletes, invalidations)`:
- **uploads**: list of `Upload(key, content_type, cache_control)` for files that are new or whose MD5 differs from the remote ETag (remote ETags may be quoted: `"abc…"`). Order: **long-cached assets first, then everything else, HTML last** (so a new `index.html` never points to assets that aren't uploaded yet); alphabetical within each group.
- **deletes**: remote keys not in `local` (sorted) when `delete=True`, else `[]` — the deploy script runs deletes **after** uploads and invalidation.
- **invalidations**: CloudFront paths (with a leading `/`) for uploaded or deleted files that are **not** immutable. `index.html` also invalidates its directory path (`/` for root `index.html`, `/docs/` for `docs/index.html`). If there are more than **15** paths, use `["/*"]` instead. Sorted.

Validation: local paths must be relative, use `/`, and not contain `..` segments → `ValueError`.

```bash
cd exercises
uv run pytest m5/w4/01-static-site-sync-plan
```
