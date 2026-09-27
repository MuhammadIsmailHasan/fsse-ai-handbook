# M5 · W6 · 04 — Render a Helm template

> 🚫🤖 **No-AI** · ⏱️ ~25 min

The engine at Helm's heart is fill-in-the-blanks: take a template with `{{ .Values.key }}` blanks and a values dict, and produce real YAML. Build it in `helm_render.py`.

## Function

```python
render(template: str, values: dict) -> str
```

Replace every blank of the form `{{ .Values.NAME }}` with `str(values[NAME])`:

- `NAME` is letters, digits or underscores (`\w+`).
- Allow optional spaces inside the braces: `{{.Values.x}}` and `{{  .Values.x  }}` both work.
- Convert the value with `str(...)`, so an integer `3` renders as `3`.
- If a referenced `NAME` is **not** in `values`, raise `KeyError(NAME)`.
- Text with no blanks is returned unchanged.

Example:

```python
render("replicas: {{ .Values.replicas }}", {"replicas": 3})
# -> "replicas: 3"
```

```bash
cd exercises
uv run pytest m5/w6/04-helm-render
```
