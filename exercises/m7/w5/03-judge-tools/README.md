# Module 7 · W5 · Using a Judge, and Checking the Judge

> 🚫🤖 **No-AI** · ⏱️ ~60 min · no API key needed

Some answers cannot be graded by string matching: "is this reply correct, polite and complete?". A language model can act as a **judge**: it gets the question, a reference answer, the answer and a **rubric**, and returns a score. That is powerful and cheap, but a judge is a model too. Before trusting its numbers, **measure it against humans**.

| Tool | Question it answers |
|---|---|
| `judge_prompt`, `parse_judge` | build the prompt; read the reply safely (fences, extra words, a score that is not an integer 1–5 is rejected) |
| `accuracy`, `cohens_kappa` | how often does the judge agree with humans, **beyond luck**? A judge that says "pass" to everything can reach 90% accuracy on a mostly-passing set, and kappa 0 |
| `confusion_matrix` | which mistakes: too strict or too lenient? |
| `swap_consistency` | **position bias**: ask a pairwise judge "A or B?" in both orders; a fair judge picks the same *answer* either way |
| `best_threshold` | which score counts as "pass" so the judge best matches the humans |

```text
kappa  <0.2 poor · 0.2–0.4 fair · 0.4–0.6 moderate · 0.6–0.8 good · >0.8 very good (rule of thumb)
```

```bash
cd exercises
uv run pytest m7/w5/03-judge-tools
```
