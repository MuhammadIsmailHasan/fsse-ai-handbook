# Module 7 · W2 · Prompts as Code

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

A prompt is source code that happens to be written in English. Give it what you give other code: **inputs that are checked**, **versions**, and **tests**.

| Piece | Does |
|---|---|
| `render(template, vars)` | fill `{{name}}` placeholders — **strictly**: a missing or unused variable is an error, not a silent hole |
| `wrap_untrusted(text)` | put user text between tags as *data*, and stop it from closing the tag early |
| `fingerprint(template)` | a short id for the exact prompt text, to log with every answer |
| `PromptRegistry` | register `name@1.2.0`, ask for a version or the latest (`1.10.0` is newer than `1.9.0`) |
| `check_cases(render_fn, cases)` | regression checks: must contain, must **not** contain, maximum length |

```text
render("Reply in {{language}}.", {"lang": "id"})
→ PromptError: missing: language        (a typo caught at once instead of "Reply in .")
```

```bash
cd exercises
uv run pytest m7/w2/01-prompt-templates
```
