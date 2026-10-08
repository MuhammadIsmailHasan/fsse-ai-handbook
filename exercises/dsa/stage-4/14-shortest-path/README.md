# DSA · Stage 4 · Shortest Path with BFS

> 🟡 Medium · 🚫🤖 No-AI · Target: O(V + E)

When every edge counts the same (one hop, one move, one letter), **BFS finds the shortest path**. It reaches all nodes 1 step away, then all nodes 2 steps away, and so on, so the first time it reaches a node is the fewest steps.

```text
        2 — 3
       /     \          shortest 1 → 4  =  2 steps  (1 → 5 → 4)
      1       4
       \     /
        5 ——
```

| Function | Does |
|---|---|
| `distances_from(graph, start)` | `{node: steps}` for everything reachable; record the distance when you first see a node |
| `shortest_path_length(graph, a, b)` | fewest edges, or `-1` |
| `shortest_path(graph, a, b)` | the path itself: remember each node's **parent**, then walk back from the goal |
| `word_ladder_length(begin, end, words)` | "hit" → "hot" → "dot" → "dog" → "cog": nodes are words, edges are one-letter changes |

For the word ladder, comparing every pair of 5,000 words is 12 million checks. Instead, for each position try the 26 letters and look the new word up in a set.

```bash
cd exercises
uv run pytest dsa/stage-4/14-shortest-path
```
