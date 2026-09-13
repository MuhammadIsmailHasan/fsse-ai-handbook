# M1 · W0 · 07 — Bug Hunt

> 🚫🤖 **No-AI** · ⏱️ ~40 min · Lesson: *Reading Errors & Debugging Basics*

`buggy_report.py` has **5 bugs**. The tests describe the correct behavior.

1. Run the tests and read the failures **bottom-up**.
2. Form a hypothesis. Confirm it with `print(f"{variable=}")` or `breakpoint()`.
3. Fix the specific line. **Don't rewrite the functions.**
4. Note each bug: *error → cause → fix*.

```bash
cd exercises
uv run pytest m1/w0/07-debugging
uv run pytest m1/w0/07-debugging -k average   # run only tests with "average" in the name
```
