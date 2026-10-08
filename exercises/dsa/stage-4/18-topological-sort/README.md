# DSA · Stage 4 · Topological Sort (Order With Dependencies)

> 🟡 Medium · 🚫🤖 No-AI · Target: O(V + E log V)

Install a package after the packages it needs. Run a build step after the steps it depends on. Take a course after its prerequisites. These are **directed** graphs: an edge `a → b` means "`a` must come first". A **topological order** lists every node so that all edges point forward. It exists only if there is **no cycle**.

**Kahn's algorithm** is a BFS on "ready" nodes:

```text
edges: 0→1  0→2  1→3  2→3

in-degree:  0:0  1:1  2:1  3:2
ready = [0]            take 0  → lower 1 and 2 → both reach 0 → ready = [1, 2]
take 1 → lower 3 (2→1)         take 2 → lower 3 (1→0) → ready = [3]      order: 0 1 2 3
```

If, at the end, you have taken fewer than `n` nodes, the rest are stuck in a **cycle**.

| Function | Does |
|---|---|
| `topo_order(n, edges)` | a valid order, smallest ready node first (use a heap); `None` on a cycle |
| `can_finish(num_courses, prerequisites)` | is there no circular requirement? Pairs are `(course, needs)` |
| `min_semesters(n, edges)` | how many rounds if you can do all ready tasks at once (take the queue one round at a time); `-1` on a cycle |

```bash
cd exercises
uv run pytest dsa/stage-4/18-topological-sort
```
