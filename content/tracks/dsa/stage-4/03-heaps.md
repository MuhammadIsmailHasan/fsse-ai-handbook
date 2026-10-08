---
title: "Heaps & Priority Queues"
summary: "Always get the smallest (or largest) item fast — how a heap lives in a plain list, sift up and sift down, Python's heapq, and the patterns it unlocks: top-k, merging sorted inputs, schedulers and the running median."
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 180
tags: [dsa, heap, priority-queue, heapq, top-k, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **heap** and a **priority queue** are
- How a heap fits in a **plain list**, and how **sift up / sift down** keep it correct
- Python's **`heapq`**: `heappush`, `heappop`, `heapify`, `nsmallest`
- Four patterns: **top-k**, **merge k sorted inputs**, **schedulers**, **running median**
- When a heap is the right tool, and when it is not
- 🧭 How to recognize a heap problem

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Heap** | A tree where every parent is smaller (or larger) than its children | Tumpukan prioritas |
| **Priority queue** | A line where the most important item always goes first | Antrean prioritas |
| **Min-heap / max-heap** | The smallest / the largest item is on top | Terkecil / terbesar di atas |
| **Sift up** | Move a new item up until its parent is smaller | Naik ke atas |
| **Sift down** | Move an item down, swapping with its smaller child | Turun ke bawah |
| **Heapify** | Turn a whole list into a heap in O(n) | Mengubah list jadi heap |
| **Top-k** | The k best items out of many | k terbaik |

## 🧠 The big idea

A heap is the **queue at a hospital emergency room**. People do not leave in the order they arrive. The most urgent patient is always seen next. A new person comes in, and the nurse puts them in the right place in the line. When the doctor is free, the most urgent one is called. Nobody needs the *whole* line sorted. You only need to know who is **next**.

That is the point of a heap. A sorted list keeps everything in order, which is more work than you need. A heap keeps only enough order to give you the best item quickly: O(1) to look, O(log n) to add or remove.

## ❓ Why it matters

"Give me the best one, now, while new items keep arriving" is everywhere:

- **job queues and schedulers** (the next task by priority or by time),
- **top-k**: the 10 most popular products, the 5 slowest requests,
- **merging** sorted logs from many servers into one timeline,
- **shortest path** algorithms such as Dijkstra (a well-known graph algorithm),
- **timers and rate limiters** (the next timeout to fire),
- the **running median** of a live metric.

Sorting everything each time is O(n log n). A heap pays only O(log n) per change.

## 📖 Step by step

### 1. A tree stored in a list

A heap is a binary tree where **every parent is ≤ both children** (min-heap). It is also *complete* (filled row by row, left to right), so it fits in a list with no node objects:

```text
index:   0  1  2  3  4  5
items: [ 1, 3, 2, 7, 4, 5 ]          1
                                    / \
parent of i = (i - 1) // 2         3   2
children    = 2i + 1, 2i + 2      / \  /
                                 7  4 5
```

Note: it is **not sorted**. 3 comes before 2. The only promise is "the parent wins", so `items[0]` is always the smallest.

### 2. Push: sift up

Add the new item at the end, then move it up while it is smaller than its parent.

```python
def push(self, value):
    items = self.items
    items.append(value)
    i = len(items) - 1
    while i > 0:
        parent = (i - 1) // 2
        if items[parent] <= items[i]:
            break
        items[parent], items[i] = items[i], items[parent]
        i = parent
```

The tree has about log₂ n levels, so this is **O(log n)**.

### 3. Pop: sift down

The smallest is `items[0]`. Take it out, move the **last** item to the top, then push it down, always swapping with the **smaller** child.

```python
def pop(self):
    items = self.items
    smallest = items[0]
    last = items.pop()
    if items:
        items[0] = last
        i, n = 0, len(items)
        while True:
            left, right, small = 2 * i + 1, 2 * i + 2, i
            if left < n and items[left] < items[small]:
                small = left
            if right < n and items[right] < items[small]:
                small = right
            if small == i:
                break
            items[i], items[small] = items[small], items[i]
            i = small
    return smallest
```

Also **O(log n)**. Why swap with the *smaller* child? So the new parent is still smaller than the other child.

### 4. Use `heapq` in real code

Python gives you a min-heap on a plain list:

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)
heap[0]                    # 1   (peek)
heapq.heappop(heap)        # 1

numbers = [5, 1, 3, 9, 2]
heapq.heapify(numbers)     # O(n), in place
heapq.nsmallest(2, numbers)   # [1, 2]
heapq.nlargest(2, numbers)    # [9, 5]
```

**Need a max-heap?** Push the **negative** (`-x`) and negate again when you pop. **Need to order by something else?** Push tuples: `(priority, item)`. Tuples compare left to right, so add a tie-breaker (an index) if items cannot be compared.

### 5. Pattern: top-k

Keep a **min-heap of size k**. It holds the k best so far, and its top is the weakest of them, the one to beat.

```python
def k_largest(nums, k):
    heap = []
    for n in nums:
        if len(heap) < k:
            heapq.heappush(heap, n)
        elif n > heap[0]:
            heapq.heapreplace(heap, n)       # pop the smallest and push n, in one step
    return sorted(heap, reverse=True)
```

Time **O(n log k)** and space **O(k)**. For "top 10 of 300,000" it beats sorting everything. It also works on a **stream** you cannot hold in memory. (For the k-th largest of a stream, the top of this heap *is* the answer.)

### 6. Pattern: merge k sorted inputs

Put the **front item of each input** in a heap. The smallest is the next output. Then push the next item from the same input.

```python
def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        value, i, j = heapq.heappop(heap)
        out.append(value)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out
```

Time **O(N log k)** for N items in k inputs. The heap never holds more than k items, so it also works for log files too big for memory. The same idea gives the *k smallest pair sums*.

### 7. Pattern: schedulers

A heap of `(time, task)` always tells you the **next thing to do**: the next timer, the next retry, the highest-priority job. Pop it, run it, and push any follow-up. Meeting-room and CPU scheduling questions use a heap of **end times** to see which room frees up first.

### 8. Pattern: running median (two heaps)

Split the numbers into a **max-heap of the smaller half** and a **min-heap of the larger half**, with sizes kept equal (or one larger). The median sits at the tops.

```text
smaller half (max-heap) | larger half (min-heap)
        [1, 2, 3]       |       [5, 8, 9]          median = (3 + 5) / 2
```

`add` is O(log n), `median` is O(1). Sorting after every number would be far slower.

### 9. Greedy with a heap

"Always take the cheapest option now" is often a heap. Joining ropes at the lowest total cost: always join the **two shortest** ropes, put the result back, repeat. This is how Huffman compression builds its codes.

### 10. Cost, and what a heap cannot do

| Operation | Time |
|---|---|
| Peek smallest | O(1) |
| Push / pop | O(log n) |
| Build from a list (`heapify`) | O(n) |
| Top-k of n items | O(n log k) |
| Search for an arbitrary value | **O(n)** — a heap is not for lookup |
| Get everything in sorted order | O(n log n) |

A heap does **not** keep all items sorted, and it cannot find or delete an arbitrary item quickly. If you need "next larger than x" or a range, use a BST. If you need lookup by key, use a hash map.

:::tip[🧭 How to spot a heap problem]
- Words like **k-th largest/smallest, top k, most frequent, closest k**.
- "**Always the next smallest/earliest/highest priority**" while the data keeps changing.
- **Merge** several sorted lists, logs or streams.
- A **median** or other running statistic of a stream.
- A **greedy** choice: "take the cheapest/shortest/earliest first".

You need *all* the items sorted once? Just sort. You need lookup, or a range? Hash map or BST.
:::

### Choosing your setup

| Need | Use |
|---|---|
| Only the best item, again and again | heap |
| Top k of a big or endless input | min-heap of size k |
| Merge k sorted inputs | heap of the front items |
| Everything sorted, once | `sorted()` |
| Lookup by key | hash map |
| Next larger than x, ranges | BST / sorted container |
| Max-heap in Python | push negatives |

- ✅ Schedulers, top-k, merging, running statistics, Dijkstra-style algorithms.
- 🚫 Searching for a value, or needing the whole collection in order.
- 🚫 A tiny list where `min()` or `sorted()` is simpler and fast enough.

## ⚠️ Common mistakes

- Thinking a heap is sorted (only `items[0]` is guaranteed).
- A max-heap by accident: `heapq` is always a min-heap. Push `-x` for a max-heap.
- Pushing objects that cannot be compared, so ties crash. Add an index as a tie-breaker.
- Using a heap of size n for top-k (O(n log n)). Keep it at size **k**.
- Using `heap[1]` as the second smallest. It is not guaranteed.
- Searching for or removing a value in the middle of a heap.

## 🏆 Best practices

- [ ] Ask: "do I need everything sorted, or only the next best item?"
- [ ] For top-k, keep a heap of size k and compare with `heap[0]`.
- [ ] Wrap items as `(priority, tie_breaker, item)` when priorities can be equal.
- [ ] Say the costs: O(log n) per push/pop, O(n) to heapify, O(n log k) for top-k.
- [ ] Use `heapq` in real code; know how sift up and sift down work for interviews.
- [ ] Mention when a sorted list, hash map or BST fits better.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a friend why a hospital emergency queue is a better picture of a heap than a sorted list. What does the nurse *not* need to know?

## 📐 Design it

CareerPilot sends reminders: "follow up on this application in 5 days". Thousands of reminders have different due times, and users add and cancel them all the time. A worker must wake up, send every reminder that is due, and sleep until the next one. Design the data structure and the worker loop. Say how you handle cancellation, and what changes when there are several workers.

:::quiz
Show a possible design

- **Min-heap keyed by due time:** entries `(due_time, reminder_id)`. Push is O(log n). The top is always the **next reminder to send**.
- **Worker loop:** peek the top. If `due_time <= now`, pop it and send it; repeat. If not, **sleep until `due_time`** (or until a new, earlier reminder is added) instead of polling every second.
- **Cancellation:** a heap cannot remove from the middle quickly. Use **lazy deletion**: keep a set of cancelled ids; when you pop a cancelled one, skip it. The heap is cleaned as you go.
- **Updating a due time:** push a new entry and mark the old one invalid (same trick).
- **Many workers / restarts:** an in-memory heap is lost on restart and not shared. Store reminders in the database (index on `due_time`) or a queue with delayed delivery; workers fetch "the next due" with `SELECT ... WHERE due_time <= now() ORDER BY due_time FOR UPDATE SKIP LOCKED`. The idea is still "give me the earliest".
- **Ties:** add the reminder id as a tie-breaker so two entries with the same time never compare their payloads.
- **Cost:** push/pop O(log n); one sleep timer instead of a busy loop.

**Rule shown:** a heap answers "what is next?" cheaply while items arrive and leave; deletion is handled lazily.
:::

### 📝 Self-review checklist

- [ ] I explained why a heap, not a sorted list or a scan
- [ ] The worker sleeps until the next due time instead of polling
- [ ] Cancellation is handled (lazy deletion or a database)
- [ ] Restarts and several workers are considered

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s4-heap-basics" title="Build a Min-Heap" difficulty="easy" path="exercises/dsa/stage-4/09-heap-basics"}
Write push (sift up), pop (sift down), peek and heap sort on a plain list — no `heapq`.
:::

:::problem{id="dsa-s4-top-k" title="Top K with a Heap" difficulty="medium" path="exercises/dsa/stage-4/10-top-k"}
The k largest values, the k most frequent words, and the k-th largest of a stream, in O(n log k).
:::

:::problem{id="dsa-s4-merge-k-sorted" title="Merge Sorted Inputs with a Heap" difficulty="medium" path="exercises/dsa/stage-4/11-merge-k-sorted"}
Merge k sorted lists, merge infinite streams lazily, and find the k smallest pair sums.
:::

:::problem{id="dsa-s4-median-and-ropes" title="Running Median & Joining Ropes" difficulty="hard" path="exercises/dsa/stage-4/12-median-and-ropes"}
Stretch: the median of a growing set with two heaps, and the cheapest way to join ropes.
:::

:::hints
- Heap indexes: parent `(i - 1) // 2`, children `2*i + 1` and `2*i + 2`.
- Sift down: pick the **smaller** child, and stop when neither child is smaller than the item.
- Top-k: `if len(heap) < k: heappush`, else `if n > heap[0]: heapreplace(heap, n)`.
- Most frequent with ties: key `(-count, word)` so a bigger count wins and then the smaller word.
- Merge: push tuples `(value, list_index, position)`; after a pop, push the next item of the **same** list.
- Lazy merge: after yielding a value, read **one** item from that same stream and `heapreplace`, or `heappop` when the stream ends.
- Smallest pair sums: start with `(a[0] + b[0], 0, 0)`; after popping `(i, j)` push `(i, j + 1)`, and push `(i + 1, 0)` only when `j == 0`.
- Median: add to the max-heap (negated), move its top to the min-heap, and if the min-heap is bigger move its top back.
- Ropes: pop two, add them to the total, push their sum back.
:::

## ✅ Quick check

:::quiz
Why is a heap faster than sorting when you only need the top 10 of 300,000 items?

A min-heap of size 10 touches each item once and costs O(log 10) per item that needs to enter the heap: O(n log k) in total, with only 10 items in memory. Sorting everything costs O(n log n) and stores all the items, even though you only want 10.
:::

:::quiz
Is a heap a sorted list? What is guaranteed?

No. Only the heap rule is guaranteed: every parent is less than or equal to its children (for a min-heap), so the smallest item is at index 0. The other items are only partly ordered. To get a sorted result you pop repeatedly.
:::

:::quiz
`heapq` is a min-heap. How do you get the largest item first?

Push the negative of each number (`-x`) and negate again after popping. For tuples, negate the priority part. The smallest negative number is the largest original number.
:::

## 📚 Keep learning

- [Python docs: heapq](https://docs.python.org/3/library/heapq.html)
- [VisuAlgo: Binary heap (interactive)](https://visualgo.net/en/heap)
- [Wikipedia: Priority queue](https://en.wikipedia.org/wiki/Priority_queue)
