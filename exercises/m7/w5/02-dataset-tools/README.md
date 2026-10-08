# Module 7 · W5 · A Dataset You Can Trust

> 🚫🤖 **No-AI** · ⏱️ ~50 min · no API key needed

Your eval is only as good as its test set. Four checks protect it:

| Function | Protects against |
|---|---|
| `validate_dataset(cases)` | broken cases: no id, empty input, no expected answer, bad tags, **duplicate ids** |
| `assign_split(id, ratios)` | the split must be **stable**: a hash of the id decides `dev` or `test`, so adding cases never moves old ones |
| `coverage(cases, required_tags)` | holes: no case for typos, for another language, for **unanswerable** questions; and thin spots with only 1–2 cases |
| `find_leaks(dev, test)` | **leakage**: a test question that is almost a copy of one you tuned on makes the score look better than it is |

```text
tune on DEV  ──►  report on TEST (never touched while tuning)
              if TEST contains near-copies of DEV, the number is a lie
```

```bash
cd exercises
uv run pytest m7/w5/02-dataset-tools
```
