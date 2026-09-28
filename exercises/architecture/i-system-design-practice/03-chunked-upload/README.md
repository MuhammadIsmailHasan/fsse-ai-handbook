# Architecture · I · Resumable Chunked Upload

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build the tracker behind a resumable upload: chunks arrive by index (maybe out of order, maybe re-sent), and the upload finishes only when every chunk is present.

| Method | Does |
|---|---|
| `receive(index, data)` | Store a chunk → `"stored"` / `"duplicate"`; `IndexError` if out of range |
| `missing()` | Sorted indices not yet received |
| `is_complete()` | True once all chunks are in |
| `assemble()` | Data in index order; `ValueError` if incomplete |

The tests re-send a duplicate chunk (harmless) and finish an upload whose chunks arrive out of order — the point of resumable uploads.

```bash
cd exercises
uv run pytest architecture/i-system-design-practice/03-chunked-upload
```
