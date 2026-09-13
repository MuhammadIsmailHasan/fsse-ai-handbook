# DSA · Stage 3 · Rainwater on a Skyline

> 🔴 Stretch · 🚫🤖 No-AI · Target: O(n) time, O(1) extra space

Building heights along a street form an elevation map (each building is 1 unit wide). After rain, how many units of water are trapped between buildings?

```python
trapped_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])   # 6
trapped_water([4, 2, 0, 3, 2, 5])                     # 9
```

Water above position `i` = `min(highest to the left, highest to the right) - height[i]` (if positive). Computing both maxima with two extra arrays is O(n) space — can two pointers and two running maxima do it in O(1)?

```bash
cd exercises
uv run pytest dsa/stage-3/04-trapping-rain-water
```
