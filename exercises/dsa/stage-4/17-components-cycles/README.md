# DSA · Stage 4 · Components, Cycles and Union-Find

> 🟡 Medium · 🚫🤖 No-AI · Target: near O(1) per union (O(α(n)))

Three basic questions about an **undirected** graph: how many separate groups does it have, does it contain a cycle, and is it a tree?

**Union-Find** (also called Disjoint Set Union) answers all three with one tiny tool. Every node starts as its own group. `union(a, b)` merges two groups. `find(x)` tells you the group's leader.

```text
start        union(0,1)    union(1,2)    union(0,2)
0  1  2  3     [0,1]  2  3   [0,1,2]  3    already together → a CYCLE
5 groups       4 groups      3 groups
```

Two tricks make it almost O(1): **path compression** (while walking up to the leader, point every node straight at it) and **union by size** (attach the smaller group under the bigger one). Write `find` with a loop — a chain of 200,000 nodes would crash recursion.

| Function | Does |
|---|---|
| `UnionFind(n)` | `find`, `union` (returns `True` if it merged two groups), `count` |
| `count_components(n, edges)` | `n` minus the number of successful unions |
| `has_cycle(n, edges)` | an edge whose two ends are **already together** closes a cycle |
| `is_valid_tree(n, edges)` | exactly `n - 1` edges and a single group |

```bash
cd exercises
uv run pytest dsa/stage-4/17-components-cycles
```
