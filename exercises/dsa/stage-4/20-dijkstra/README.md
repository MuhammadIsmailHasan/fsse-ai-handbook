# DSA · Stage 4 · Cheapest Routes (Dijkstra)

> 🔴 Hard · 🚫🤖 No-AI · Target: O((V + E) log V)

BFS counts **steps**. But roads have different lengths, flights have different prices, and network links have different delays. When edges have **weights** (zero or more), use **Dijkstra's algorithm**: it is BFS with a **min-heap** instead of a queue, so it always expands the cheapest node found so far.

```text
graph: A→B 4, A→C 1, C→B 2, B→D 1, C→D 7

heap: (0, A)
pop A (0)  → push (4, B) (1, C)
pop C (1)  → push (3, B) (8, D)
pop B (3)  → push (4, D)             B costs 3, not 4: the longer-looking way is cheaper
pop D (4)  ✔
```

The first time you **pop** a node from the heap, its cost is final. If you pop a node you have already finished, just skip it (lazy deletion). Dijkstra needs weights that are **not negative**.

| Function | Does |
|---|---|
| `dijkstra(graph, source)` | `{node: cheapest cost}` for every reachable node |
| `cheapest_route(graph, a, b)` | `(cost, path)` or `None`; keep a `parent` for each node |
| `network_delay_time(times, n, k)` | how long until all `n` nodes receive a signal from `k`, or `-1` |

```bash
cd exercises
uv run pytest dsa/stage-4/20-dijkstra
```
