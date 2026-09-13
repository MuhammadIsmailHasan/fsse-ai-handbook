# M2 · W1 · 02 — Write CareerPilot's README

> 🚫🤖 **No-AI** · ⏱️ ~45 min

Write `README.md` **in this folder** for your CareerPilot Phase 1 CLI. The tests check:

1. Exactly **one** level-1 heading (`# …`) and it's the first line
2. A description paragraph right after the title (not empty, at least 10 words)
3. These level-2 sections (any order, emojis allowed): **Features**, **Tech Stack**, **Architecture**, **Getting Started**, **Usage**, **Testing**
4. A fenced ` ```bash ` block containing `python cli.py`
5. At least one **table**
6. A ` ```mermaid ` diagram
7. Only **relative** or `https://` links (no `http://`, no `localhost`)
8. No secrets: nothing that looks like `password=`, `secret=`, `api_key=` or a `.env` value

```bash
cd exercises
uv run pytest m2/w1/02-markdown-readme
```
