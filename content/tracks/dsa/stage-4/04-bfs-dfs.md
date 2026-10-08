---
title: "Graphs: BFS & DFS"
summary: "Model things as graphs (even grids), remember what you have visited, and explore with a queue (BFS, shortest paths) or a stack (DFS, islands and flood fill) — plus multi-source BFS and the habit of avoiding deep recursion."
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 210
tags: [dsa, graphs, bfs, dfs, grids, shortest-path, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **graph** is, and how to store it as an **adjacency list**
- Why you need a **visited** set (cycles!)
- **BFS** with a queue and **DFS** with a stack, and how they differ
- BFS for the **shortest path** when every step costs the same
- Treating a **grid** as a graph (islands, flood fill, mazes)
- **Multi-source BFS**, and why to avoid deep recursion
- 🧭 How to recognize a graph problem

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Graph** | Nodes connected by edges | Graf |
| **Node (vertex)** | One thing: a person, a page, a city | Simpul |
| **Edge** | A connection between two nodes | Sisi |
| **Directed / undirected** | One-way edges / two-way edges | Berarah / tak berarah |
| **Neighbour** | A node you can reach with one edge | Tetangga |
| **Visited** | Nodes you have already seen, so you do not loop | Sudah dikunjungi |
| **BFS** | Explore nearest nodes first, using a queue | Penelusuran melebar |
| **DFS** | Go as deep as you can first, using a stack | Penelusuran mendalam |

## 🧠 The big idea

A graph is a **city map**: places (nodes) and roads (edges). A tree is a city with only one road to each place. A graph can have loops, so you might walk in circles forever. The fix is a simple habit: **mark every place you have visited**.

Now two ways to explore from your home:

- **BFS** is a **ripple in a pond**. You visit everything 1 street away, then everything 2 streets away, then 3. The first time you reach a place, you used the fewest streets. You need a **queue**: first come, first served.
- **DFS** is **walking through a maze with a ball of string**. You follow one road as far as it goes, and only when you hit a dead end do you go back to the last crossing. You need a **stack**: last in, first out (or recursion, which is a hidden stack).

## ❓ Why it matters

Graphs are everywhere, once you start looking:

- **social networks** (friends of friends), **web links** (crawlers),
- **maps and routing**, **flight connections**,
- **dependencies** between packages, tasks and database tables,
- **a game board**, a **photo** (pixels), a **maze**, an **office floor plan**,
- **Kubernetes, microservices, and Terraform** all draw dependency graphs.

BFS and DFS are the two basic moves behind almost every graph algorithm. Interviewers love them because the idea is small, and the traps (no visited set, recursion too deep) are easy to see.

## 📖 Step by step

### 1. Store a graph as an adjacency list

A dictionary: each node maps to the list of its neighbours.

```python
def build_graph(edges, directed=False):
    sets = {}
    for a, b in edges:
        sets.setdefault(a, set()).add(b)
        sets.setdefault(b, set())
        if not directed:
            sets[b].add(a)              # undirected: the road goes both ways
    return {node: sorted(neighbours) for node, neighbours in sets.items()}
```

```text
edges: (1,2) (1,3) (2,4) (3,4) (4,5)

        1
       / \          graph = {1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3, 5], 5: [4]}
      2   3
       \ /
        4 — 5
```

For `n` nodes and `m` edges the list uses O(n + m) space. An alternative is an adjacency **matrix** (n × n), which wastes space unless the graph is very dense.

### 2. BFS: a queue and a visited set

```python
from collections import deque

def bfs_order(graph, start):
    seen, order, queue = {start}, [], deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)             # mark when you ADD it, not when you pop it
                queue.append(nxt)
    return order
```

Marking a node as seen **when you put it in the queue** keeps each node from entering twice. Time is **O(V + E)**: every node and every edge is looked at once.

### 3. DFS: a stack (no recursion needed)

```python
def dfs_order(graph, start):
    seen, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for nxt in reversed(graph.get(node, [])):   # reversed, so the smallest is visited first
            if nxt not in seen:
                stack.append(nxt)
    return order
```

This is the *same* code as BFS with the queue swapped for a stack. The recursive version is shorter, but Python allows only about 1,000 nested calls, so a path of 50,000 nodes crashes it. Prefer the stack when the graph can be deep.

```python
def dfs_recursive(graph, node, seen):    # short, fine for small or shallow graphs
    seen.add(node)
    for nxt in graph[node]:
        if nxt not in seen:
            dfs_recursive(graph, nxt, seen)
```

### 4. BFS gives the shortest path

When every edge costs the same (one hop, one move), the first time BFS reaches a node is the **fewest steps**. Record the distance when you first see a node, and the parent if you need the path itself.

```python
def distances_from(graph, start):
    dist, queue = {start: 0}, deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt not in dist:                 # "not in dist" is the visited check
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    return dist
```

To get the path, store `parent[nxt] = node`, and walk back from the goal to the start. DFS does **not** give shortest paths.

Many puzzles are shortest-path problems in disguise. A **word ladder** ("hit" → "hot" → "dot" → "dog" → "cog") has words as nodes and one-letter changes as edges.

### 5. A grid is a graph

A map, a photo or a game board: each cell is a node, and its neighbours are up, down, left and right. You do not build the graph. You compute the neighbours:

```python
for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    nr, nc = r + dr, c + dc
    if 0 <= nr < rows and 0 <= nc < cols:      # stay inside the grid
        ...
```

**Counting islands:** for every land cell you have not seen, add 1 and flood its whole island with a stack.

```python
def count_islands(grid):
    rows, cols = len(grid), len(grid[0]) if grid else 0
    seen, islands = set(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                islands += 1
                seen.add((r, c))
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == "1" and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
    return islands
```

The same flood is the **paint bucket** in an image editor (flood fill), and it measures the **area** of the biggest island.

### 6. Multi-source BFS

What if many cells can be the start: every rotten orange, every `0` in a matrix, every fire in a forest? Put **all of them in the queue at the beginning**. One BFS then gives each cell its distance to the *nearest* source.

```python
queue = deque((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2)
minutes = 0
while queue and fresh:
    for _ in range(len(queue)):          # one whole round = one minute
        ...
    minutes += 1
```

Running a separate BFS from every cell would cost O(cells²). Multi-source BFS costs O(cells).

### 7. Rounds: counting levels

Process the queue **one round at a time** (`for _ in range(len(queue))`). After round `k` you have reached everything `k` steps away. The number of rounds is the distance, the number of minutes, or the number of levels.

### 8. Cost and limits

| | Time | Space |
|---|---|---|
| BFS / DFS on an adjacency list | O(V + E) | O(V) |
| Grid with R rows and C columns | O(R × C) | O(R × C) |
| Shortest path (equal edges) | O(V + E) | O(V) |

BFS is for **equal** step costs. If edges have different weights (roads of different lengths), you need Dijkstra's algorithm, which is BFS with a heap instead of a queue.

:::tip[🧭 How to spot a graph problem]
- Things **connected to other things**: friends, links, roads, prerequisites, dependencies.
- A **grid** or board where you move up, down, left and right.
- Words like **connected, reachable, path, shortest, minimum number of steps/moves, islands, regions**.
- A puzzle where each state can change into a few other states (a word ladder, a lock, a sliding game): the states are nodes.

"Fewest steps" → **BFS**. "Does a path exist / count regions / explore everything" → BFS or DFS, both fine. "All possible paths" → DFS with backtracking.
:::

### Choosing your setup

| Need | Use |
|---|---|
| Shortest path, equal step costs | BFS (queue) |
| Reachable? Count regions? Flood fill? | DFS (stack) or BFS |
| Many starting points at once | multi-source BFS |
| Very deep graph | stack or queue, not recursion |
| Different edge weights | Dijkstra (heap) |
| Cycle detection, ordering, bipartite | next lesson |

- ✅ Connectivity, regions, fewest steps, dependency exploration.
- 🚫 BFS for shortest paths with different edge costs.
- 🚫 Recursion on a graph that can be 50,000 deep.

## ⚠️ Common mistakes

- No `visited` set, so the search loops forever on a cycle.
- Marking a node as seen only **when you pop it** (it enters the queue many times).
- Using DFS and expecting the shortest path.
- Forgetting grid bounds (`0 <= r < rows`) or checking them after reading the cell.
- Reading a cell `(r, c)` as `grid[c][r]`.
- Recursion on a 500 × 500 grid that is all land.
- Changing the input grid without saying so (copy it, or use a `seen` set).
- `list.pop(0)` as a queue (O(n)); use `collections.deque`.

## 🏆 Best practices

- [ ] Draw the graph for the example: what are the nodes, what are the edges?
- [ ] Start with the three pieces: **data structure** (queue or stack), **visited**, **neighbours**.
- [ ] Mark visited when you **add** a node, not when you remove it.
- [ ] Use `deque` for BFS. Use a list as a stack for DFS.
- [ ] Say the cost: O(V + E), or O(rows × cols) for a grid.
- [ ] Test on: one node, a cycle, a disconnected graph, and a long path.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain BFS and DFS to a friend using a pond ripple and a maze with string. Why does BFS find the shortest path and DFS not?

## 📐 Design it

CareerPilot wants a **"people you could ask for a referral"** feature. A user's contacts form a network: you know some people, they know others. Given a company, find the people who work there and are **closest to the user** (fewest introductions), and show the introduction chain. Design the data and the algorithm. What if the network has 5 million people?

:::quiz
Show a possible design

- **Model:** people are nodes, "knows" is an edge (undirected). Store an **adjacency list**: `person_id → [contact ids]`.
- **Algorithm:** **BFS from the user**. The first people BFS reaches who work at the target company are the closest. Keep a `parent` map to rebuild the chain "you → Rina → Budi → Dewi".
- **Stop early:** stop at the first level that contains a match (or after k matches). Limit the depth to about 3, since long chains are not useful introductions.
- **Output:** the chain from the `parent` map; sort ties by something useful (strength of the connection).
- **Many starts:** to find, for every company, the nearest employee, run a **multi-source BFS** from all employees of that company at once.
- **5 million people:** the whole graph may not fit in one process. Fetch neighbours **on demand** from the database or a graph store (`WHERE person_id = ?` with an index) and only for the first 2–3 levels; cache popular nodes. A *bidirectional BFS* (from the user and from the target) cuts the work a lot.
- **Cycles:** use a `visited` set so a mutual contact is not processed twice.
- **Privacy:** only show people who agreed to be discoverable.

**Rule shown:** "closest / fewest steps" in a network is BFS, with a visited set and a parent map for the path.
:::

### 📝 Self-review checklist

- [ ] Nodes and edges are named clearly
- [ ] BFS, with a reason (fewest introductions)
- [ ] Visited set and parent map are there
- [ ] Depth limit and scale are discussed

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s4-graph-traversal" title="Graph Traversal: BFS and DFS" difficulty="easy" path="exercises/dsa/stage-4/13-graph-traversal"}
Build an adjacency list, then BFS, DFS (with your own stack, on a 50,000-node path) and a reachability check.
:::

:::problem{id="dsa-s4-shortest-path" title="Shortest Path with BFS" difficulty="medium" path="exercises/dsa/stage-4/14-shortest-path"}
Distances, the shortest path itself, and a word ladder over 5,000 words.
:::

:::problem{id="dsa-s4-grid-islands" title="Grids Are Graphs: Islands and Flood Fill" difficulty="medium" path="exercises/dsa/stage-4/15-grid-islands"}
Count islands, find the biggest one, and paint-bucket fill, on a 500 × 500 grid without recursion.
:::

:::problem{id="dsa-s4-grid-shortest" title="Shortest Paths on Grids" difficulty="hard" path="exercises/dsa/stage-4/16-grid-shortest"}
Stretch: a maze, rotting oranges and distance-to-nearest-zero, using rounds and multi-source BFS.
:::

:::hints
- BFS: `deque`, `popleft`, a `seen` set, and add to `seen` **when you append**.
- DFS with a stack: push `reversed(neighbours)` so the smallest comes off the stack first.
- `has_path(a, a)` is `True`: a node reaches itself.
- Distances: `dist = {start: 0}`; `if nxt not in dist` doubles as the visited check.
- Path: keep `parent[nxt] = node`, then follow parents back from the goal and reverse the list.
- Word ladder: for each position try `a..z` and check the new word in a `set`; count words, not changes.
- Islands: loop over every cell; start a flood only on land you have not seen; mark cells seen when you push them.
- `flood_fill`: copy the image first; if the old colour equals the new colour, return the copy.
- Rotting oranges: put every rotten orange in the queue first; do one round per minute; if `fresh` is still above 0 at the end, return `-1`.
- Nearest zero: start the queue with every `0` at distance 0 and fill the other cells as BFS reaches them.
:::

## ✅ Quick check

:::quiz
Why does BFS find the shortest path in an unweighted graph, but DFS does not?

BFS visits nodes in rings: all nodes 1 step away, then 2 steps, and so on. The first time it reaches a node, it used the fewest steps. DFS follows one path as deep as it can, so it may reach a node by a long route first.
:::

:::quiz
Why must you mark a node as visited when you add it to the queue, not when you remove it?

If you wait until you pop it, the same node can be added many times by different neighbours before it is processed. That wastes time and memory, and on dense graphs it can blow up. Marking at insertion keeps every node in the queue at most once.
:::

:::quiz
What is multi-source BFS, and when do you use it?

You put all the starting points in the queue at the beginning and run one BFS. Each cell gets its distance to the nearest start. Use it when many cells can be the source (rotten oranges, zeros in a matrix, all employees of a company), instead of running a separate BFS from every cell.
:::

## 📚 Keep learning

- [VisuAlgo: Graph traversal (BFS and DFS, interactive)](https://visualgo.net/en/dfsbfs)
- [Python docs: collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Wikipedia: Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
