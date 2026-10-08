# DSA · Stage 4 · Graph Traversal: BFS and DFS

> 🟢 Easy · 🚫🤖 No-AI · Target: O(V + E)

A **graph** is nodes connected by edges: friends on a social network, pages linked on a website, roads between cities. Unlike a tree it can have **cycles**, so you must remember which nodes you have **already visited**, or you will loop forever.

```text
graph = {1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3, 5], 5: [4]}

        1
       / \          BFS from 1 : 1 2 3 4 5     (nearest first — a queue)
      2   3         DFS from 1 : 1 2 4 3 5     (deep first   — a stack)
       \ /
        4 — 5
```

| Function | Does |
|---|---|
| `build_graph(edges, directed=False)` | adjacency list; neighbours sorted; both directions if undirected |
| `bfs_order(graph, start)` | breadth-first: a **queue** (`deque`) and a `visited` set |
| `dfs_order(graph, start)` | depth-first with your own **stack** (the test path has 50,000 nodes) |
| `has_path(graph, a, b)` | can you get from `a` to `b`? |

The only difference between BFS and DFS is **queue vs stack**.

```bash
cd exercises
uv run pytest dsa/stage-4/13-graph-traversal
```
