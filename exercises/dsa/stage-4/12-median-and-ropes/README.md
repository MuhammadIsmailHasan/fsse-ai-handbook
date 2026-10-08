# DSA · Stage 4 · Running Median & Joining Ropes

> 🔴 Hard · 🚫🤖 No-AI · Target: O(log n) per update

Two problems where **two heaps** (or one heap used greedily) beat sorting again and again.

**`MedianFinder`.** Numbers arrive one by one, and you must report the median at any moment. Sorting after every number costs O(n log n) each time. Instead split the numbers into two halves:

```text
smaller half (MAX-heap)   |   larger half (MIN-heap)
   top = biggest of the small |  top = smallest of the large
        [1, 2, 3]                    [5, 8, 9]          → median = (3 + 5) / 2

keep the sizes equal (or one larger), so the median is always at the tops
```

`heapq` only has a min-heap, so store **negated numbers** in the max-heap.

**`min_cost_to_connect(ropes)`.** Joining two ropes costs their total length. Joining long ropes early makes you pay for them many times, so always join the **two shortest** ropes first (a greedy choice; this is how Huffman coding works).

```bash
cd exercises
uv run pytest dsa/stage-4/12-median-and-ropes
```
