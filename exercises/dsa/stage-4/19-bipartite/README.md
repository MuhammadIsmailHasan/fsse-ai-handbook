# DSA · Stage 4 · Two-Colouring (Bipartite Graphs)

> 🟡 Medium · 🚫🤖 No-AI · Target: O(V + E)

Can you split people into **two teams** so that nobody who dislikes someone is on the same team? Can you assign **two time slots** so that no two conflicting exams share one? Each is the same graph question: can you paint every node with one of **two colours** so that every edge joins **different** colours? A graph with such a painting is **bipartite**.

The method: pick a node, paint it 0, and BFS. Every neighbour gets the opposite colour. If a node's neighbour already has **the same colour as the node**, you found a conflict.

```text
even cycle (works)          odd cycle (impossible)
 0 — 1                       0 — 1
 |   |                        \  /
 3 — 2                         2         the third node always clashes
colours 0 1 / 3 2 = 0 1 0 1
```

A graph is bipartite **exactly when it has no cycle with an odd number of nodes**. Remember to start a new BFS for every group (the graph may be in several pieces).

| Function | Does |
|---|---|
| `two_color(n, edges)` | colours `0/1` or `None`; the smallest node of each group is colour 0 |
| `is_bipartite(n, edges)` | `True` / `False` |
| `can_split_into_two_teams(n, dislikes)` | people are numbered from **1** |
| `has_odd_cycle(n, edges)` | the opposite of bipartite |

```bash
cd exercises
uv run pytest dsa/stage-4/19-bipartite
```
