# DSA · Stage 2 · Longest Common Prefix

> 🟡 Medium · 🚫🤖 No-AI · Target: O(total characters)

CareerPilot groups job slugs like `backend-engineer-jakarta`, `backend-engineer-remote`. Find the shared start.

`longest_common_prefix(words)` → the longest string that every word starts with.

```python
longest_common_prefix(["backend-engineer-jakarta", "backend-engineer-remote", "backend-dev"])  # "backend-"
longest_common_prefix(["data", "devops"])  # "d"
longest_common_prefix(["ml", "ai"])        # ""
longest_common_prefix([])                  # ""
```

Don't use `os.path.commonprefix` (a test checks). Stretch: can you stop as soon as a mismatch appears, without comparing every word fully?

```bash
cd exercises
uv run pytest dsa/stage-2/03-longest-common-prefix
```
