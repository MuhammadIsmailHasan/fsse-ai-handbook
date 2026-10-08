---
title: "Basic Graph Problems"
summary: "Solve the classic graph questions with one tool each — union-find for groups and cycles, Kahn's algorithm for dependency order, two-colouring for conflicts, and Dijkstra for cheapest routes — and know which tool to pick."
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 210
tags: [dsa, graphs, union-find, topological-sort, bipartite, dijkstra, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Count **connected groups** and detect **cycles** with **union-find**
- Put tasks in a valid order with **topological sort** (Kahn's algorithm)
- Check if things can be split in two with **two-colouring** (bipartite)
- Find **cheapest routes** with **Dijkstra** when edges have different costs
- Pick the right tool for a question, and say why
- 🧭 How to recognize each problem

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Connected component** | A group of nodes that can all reach each other | Komponen terhubung |
| **Cycle** | A path that comes back to where it started | Siklus |
| **Union-find** | A tool that merges groups and tells which group a node is in | Gabung-cari |
| **DAG** | Directed graph with no cycle | Graf berarah tanpa siklus |
| **Topological order** | A list where every arrow points forward | Urutan topologis |
| **In-degree** | How many arrows point into a node | Jumlah panah masuk |
| **Bipartite** | Can be coloured with two colours, no edge joins the same colour | Bipartit |
| **Weight** | The cost of an edge: distance, price, time | Bobot |

## 🧠 The big idea

After BFS and DFS you have a **toolbox**. Four everyday questions each have a small, famous tool:

- "**Are these in the same group? Did this link close a loop?**" → **union-find**, like a school where every new friendship merges two friend groups.
- "**What do I do first?**" → **topological sort**, like a recipe where you cannot bake before you mix.
- "**Can I put these into two teams with no clashes?**" → **two-colouring**, like seating two feuding families at two tables.
- "**What is the cheapest way to get there?**" → **Dijkstra**, like a navigation app that adds up the tolls and minutes.

You do not need to invent these. You need to **recognize the question** and reach for the tool.

## ❓ Why it matters

These are real jobs, not only interview puzzles:

- **Groups and cycles:** "are these two accounts connected?", detecting duplicate accounts, finding a loop in a configuration.
- **Dependency order:** `pip install`, `npm`, database migrations, Terraform, CI pipelines, build systems, spreadsheet cells. A cycle here is a real error ("circular dependency").
- **Two sides:** scheduling exams without clashes, assigning reviewers, splitting a test set.
- **Cheapest routes:** maps, network routing, flight prices, delivery costs, game AI.

They also give a clear way to talk in interviews: "this is a dependency problem, so a topological sort in O(V + E)".

## 📖 Step by step

### 1. Union-find: groups and cycles

Every node starts as its own group. `union(a, b)` merges two groups. `find(x)` returns the group's leader.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.count = n                       # number of groups

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:        # path compression: point everyone at the leader
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                     # already together
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                 # union by size: small group joins the big one
        self.size[ra] += self.size[rb]
        self.count -= 1
        return True
```

```python
def count_components(n, edges):
    uf = UnionFind(n)
    for a, b in edges:
        uf.union(a, b)
    return uf.count

def has_cycle(n, edges):
    uf = UnionFind(n)
    return any(not uf.union(a, b) for a, b in edges)   # an edge inside one group closes a loop
```

With path compression and union by size, each operation is almost O(1). A **tree** is a graph with exactly `n - 1` edges that is connected.

**Use it when:** edges arrive one by one ("add a friendship"), and you ask "same group?" or "is there a loop?". For a fixed graph, BFS/DFS also works.

### 2. Topological sort: dependency order

A directed edge `a → b` means "a must come first". A valid order puts every arrow pointing forward. It exists **only if there is no cycle**.

**Kahn's algorithm:** count the arrows pointing into each node (in-degree). Start with nodes that have none (they are *ready*). Take one, and lower the count of everything it points to. Anything that reaches 0 becomes ready.

```python
import heapq

def topo_order(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    ready = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(ready)                         # smallest first, so the result is predictable
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(ready, nxt)
    return order if len(order) == n else None    # fewer than n taken → there is a cycle
```

If you end with fewer than `n` nodes, the rest wait on each other forever: **a cycle** (`can_finish` is just this check). Take the queue **one round at a time** to answer "how many rounds if I can do all ready tasks together?" (the longest chain).

**Use it when:** "order the tasks", "can all courses be taken?", "build order", "minimum number of rounds".

### 3. Two-colouring: bipartite check

Paint a node 0, then BFS, giving each neighbour the **opposite** colour. If a neighbour already has the **same** colour as you, there is a clash.

```python
from collections import deque

def two_color(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    for start in range(n):                       # the graph may be in several pieces
        if color[start] != -1:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in adj[node]:
                if color[nxt] == -1:
                    color[nxt] = 1 - color[node]
                    queue.append(nxt)
                elif color[nxt] == color[node]:
                    return None                  # two neighbours with the same colour
    return color
```

A graph is bipartite **exactly when it has no cycle with an odd number of nodes** (a triangle, a 5-cycle). "Split into two teams where these pairs dislike each other" is this problem.

### 4. Dijkstra: cheapest routes

BFS counts steps. With **weights** (km, price, minutes, never negative), use a **min-heap** of `(cost so far, node)`. Always expand the cheapest node found so far.

```python
import heapq

def dijkstra(graph, source):
    dist = {}
    heap = [(0, source)]
    while heap:
        cost, node = heapq.heappop(heap)
        if node in dist:                         # already finished with a cheaper cost
            continue
        dist[node] = cost                        # the first pop of a node is its final cost
        for nxt, weight in graph.get(node, []):
            if nxt not in dist:
                heapq.heappush(heap, (cost + weight, nxt))
    return dist
```

```text
A→B 4, A→C 1, C→B 2, B→D 1, C→D 7

pop A (0) → push B 4, C 1
pop C (1) → push B 3, D 8
pop B (3) → push D 4        ← B costs 3 (via C), not 4
pop D (4)
```

Keep a `parent` for each node to rebuild the route. Time is **O((V + E) log V)**. Dijkstra needs non-negative weights; with negative weights use Bellman-Ford.

### 5. Choosing the tool

| Question | Tool | Time |
|---|---|---|
| Fewest steps, equal edges | BFS | O(V + E) |
| Cheapest route, weights ≥ 0 | Dijkstra (heap) | O((V + E) log V) |
| How many groups? Is there a loop? Edges arriving online | union-find | ≈ O(E) |
| Order with dependencies; is there a circular dependency? | topological sort (Kahn) | O(V + E) |
| Can it be split into two sides? | two-colouring (BFS) | O(V + E) |
| Reachable? Explore everything? | BFS / DFS | O(V + E) |

:::tip[🧭 How to spot each problem]
- **"Connected / same group / number of groups / redundant connection / is it a tree"** → union-find (or DFS).
- **"Order / prerequisites / build order / dependency / circular dependency / schedule"** → topological sort.
- **"Two groups / teams / two colours / conflicts / odd cycle"** → bipartite.
- **"Cheapest / fastest / shortest with weights / delay time / minimum cost to reach"** → Dijkstra.
- **"Fewest moves" with equal costs** → BFS.

The word **"directed"** often points to topological sort or Dijkstra. The word **"undirected"** with **"group"** points to union-find.
:::

### Choosing your setup

| Situation | Use |
|---|---|
| Data arrives as a stream of connections | union-find |
| Fixed graph, count regions | BFS/DFS or union-find |
| Many tasks with prerequisites | topological sort |
| Edge costs differ | Dijkstra |
| Edge costs equal | BFS |
| Negative edge costs | Bellman-Ford (mention it) |

- ✅ Dependencies, networks, scheduling, routing, grouping.
- 🚫 Dijkstra with negative weights.
- 🚫 Topological sort on a graph with cycles (detect it and report an error).

## ⚠️ Common mistakes

- Union-find without path compression or union by size (it becomes O(n) per call on chains).
- Recursive `find` on a chain of 200,000 nodes (use a loop).
- Forgetting a repeated edge or a self-loop (`(u, u)`) when you look for cycles.
- Topological sort: forgetting to check that all `n` nodes were taken (the cycle check).
- Reversing the direction of a prerequisite pair `(course, needs)`.
- Two-colouring only the first group and ignoring the other pieces of the graph.
- Dijkstra: marking a node final when you **push** it instead of when you **pop** it.
- Using Dijkstra on negative weights, or BFS on weighted edges.

## 🏆 Best practices

- [ ] Name the **nodes** and the **edges**, and say whether they are directed and weighted.
- [ ] Match the question to a tool with a sentence: "this is a dependency problem, so topological sort".
- [ ] State the cost: O(V + E), or O((V + E) log V) for Dijkstra.
- [ ] Handle disconnected graphs: loop over all nodes, not only node 0.
- [ ] Test on: no edges, a single node, a cycle, a self-loop, a repeated edge.
- [ ] Use loops (not recursion) for graphs that can be very deep.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate, with a recipe analogy, why a cycle in a build's dependencies means the build cannot run, and how Kahn's algorithm discovers it without ever "looking for a cycle".

## 📐 Design it

CareerPilot's Phase 5 deploys several services: `database`, `core-api`, `ai-service`, `worker`, `web`. Each needs some of the others to be healthy first. Your deploy tool must (1) decide an order, (2) start independent services **at the same time**, and (3) refuse to run if the config has a circular dependency, with a helpful message. Design the algorithm and the error message.

:::quiz
Show a possible design

- **Model:** services are nodes; an edge `a → b` means "a must be healthy before b starts". Read it from each service's `depends_on` list.
- **Algorithm:** **Kahn's topological sort, one round at a time.** Round 1: services with no dependencies (`database`). Round 2: everything that only needed those (`core-api`, `worker`, ...). All services in a round start **in parallel**. The number of rounds is the minimum deploy time in "waves".
- **Cycle detection:** if after the loop fewer services were scheduled than exist, the remaining ones depend on each other. Report them: *"Circular dependency among: ai-service, worker"*. To print the actual loop, run a DFS on the remaining nodes and follow edges until you return to a node already on the path.
- **Validation before deploying:** also check unknown names (a dependency that is not a service) and self-dependencies.
- **Deterministic output:** take ready services in alphabetical order, so the plan is the same every time and easy to review.
- **Cost:** O(V + E), trivial for tens of services.
- **Teardown:** destroy in the **reverse** order (web first, database last). Terraform and Kubernetes do the same.

**Rule shown:** "start things in dependency order, in parallel waves" is a topological sort by rounds, and leftover nodes are your cycle.
:::

### 📝 Self-review checklist

- [ ] Nodes, edges and direction are stated
- [ ] Rounds give parallel starts
- [ ] A cycle is reported clearly
- [ ] Teardown order is considered

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s4-components-cycles" title="Components, Cycles and Union-Find" difficulty="medium" path="exercises/dsa/stage-4/17-components-cycles"}
Write `UnionFind`, count groups, detect cycles (including self-loops and repeated edges) and check for a tree.
:::

:::problem{id="dsa-s4-topological-sort" title="Topological Sort" difficulty="medium" path="exercises/dsa/stage-4/18-topological-sort"}
Order tasks by dependency with Kahn's algorithm, detect circular requirements, and count the rounds needed.
:::

:::problem{id="dsa-s4-bipartite" title="Two-Colouring (Bipartite)" difficulty="medium" path="exercises/dsa/stage-4/19-bipartite"}
Colour a graph with two colours, split people into two teams, and detect odd cycles.
:::

:::problem{id="dsa-s4-dijkstra" title="Cheapest Routes (Dijkstra)" difficulty="hard" path="exercises/dsa/stage-4/20-dijkstra"}
Stretch: costs to every node, the cheapest route itself, and the time for a signal to reach the whole network.
:::

:::hints
- Union-find `find`: loop up to the root, then loop again to point every node at the root.
- `union` returns `False` when both nodes already have the same root: that is your cycle signal.
- A valid tree has exactly `n - 1` edges **and** one group; check the edge count first.
- Kahn: build `adj` and `indeg`; start with the nodes of in-degree 0 in a min-heap; `len(order) == n` means no cycle.
- `can_finish`: the pair is `(course, needs)`, so the edge is `needs → course`.
- `min_semesters`: keep the current round as a list; the next round collects nodes whose in-degree just became 0.
- Two-colouring: loop `for start in range(n)` so every group is coloured; a neighbour with the same colour means `None`.
- `can_split_into_two_teams`: people are numbered from 1; subtract 1 for nodes `0..n-1`.
- Dijkstra: `if node in dist: continue` right after the pop; set `dist[node]` at the pop, not the push.
- `cheapest_route`: push `(cost, node, previous)` and store `parent[node] = previous` when you finalize the node.
- `network_delay_time`: Dijkstra from `k`; if fewer than `n` nodes are reached return `-1`, else the largest cost.
:::

## ✅ Quick check

:::quiz
Topological sort produces fewer than n nodes. What does that mean?

The remaining nodes each wait for another remaining node, so none of them ever reaches in-degree 0. That is a cycle in the dependencies, and no valid order exists.
:::

:::quiz
Why can't Dijkstra handle negative edge weights?

Dijkstra assumes the first time it pops a node, nothing cheaper can appear later, because adding more edges only increases the cost. A negative edge can lower the cost of a node that was already finalized. Use Bellman-Ford when weights can be negative.
:::

:::quiz
How does union-find tell you an edge closes a cycle?

If both ends of the edge already have the same leader, they are already connected through other edges. Adding this edge creates a second route between them, which is a cycle.
:::

## 📚 Keep learning

- [VisuAlgo: Single-source shortest paths (Dijkstra, interactive)](https://visualgo.net/en/sssp)
- [VisuAlgo: Union-Find disjoint sets](https://visualgo.net/en/ufds)
- [Wikipedia: Topological sorting](https://en.wikipedia.org/wiki/Topological_sorting)
