# Module 7 · W5 · A Tiny Eval Harness

> 🚫🤖 **No-AI** · ⏱️ ~50 min · no API key needed

An **eval** is a fixed set of questions with checks. You run it **before** and **after** every change and compare the numbers. That is the difference between "I think it got better" and "pass rate went from 0.71 to 0.83 and nothing important broke".

| Piece | Does |
|---|---|
| graders | small functions `grader(case, output) -> bool`: `contains_all`, `not_contains`, `matches` (regex), `max_chars`, `exact_match` |
| `run_eval(system, cases, graders)` | run everything; pass rate **per grader** and **per tag**; a crash in the system counts as a failed case but does not stop the run |
| `compare_runs(old, new)` | which cases got **fixed**, which got **broken** |
| `gate(old, new, min_pass_rate)` | the release decision: block if the rate is too low **or** if too many cases broke |

```text
old: 0.67   new: 0.67        ← same rate, but "b" was fixed and "a" was broken
                                the average hides it; compare_runs shows it
```

```bash
cd exercises
uv run pytest m7/w5/01-eval-harness
```
