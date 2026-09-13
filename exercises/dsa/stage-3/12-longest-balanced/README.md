# DSA · Stage 3 · Longest Balanced Stretch

> 🔴 Stretch · 🚫🤖 No-AI · Target: O(n)

An A/B test logs which variant each visitor saw: `0` (A) or `1` (B). Find the longest stretch of **consecutive** visitors with an **equal** number of A and B.

`longest_balanced(visits)` → the length of the longest contiguous subarray with as many `0`s as `1`s.

```python
longest_balanced([0, 1, 0])            # 2
longest_balanced([0, 0, 1, 0, 1, 1, 0]) # 6
longest_balanced([1, 1, 1])            # 0
```

Treat `0` as `-1`: a balanced stretch has sum 0, so two equal prefix sums mark its ends. Store the **first** index where each prefix sum appears.

```bash
cd exercises
uv run pytest dsa/stage-3/12-longest-balanced
```
