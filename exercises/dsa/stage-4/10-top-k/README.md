# DSA · Stage 4 · Top K with a Heap

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n log k)

"Give me the top 10 out of 300,000" does **not** need a full sort. Keep a **min-heap of size k**: it holds the k best so far, and its smallest item is the one to beat.

```text
k = 3, stream: 3 1 5 12 2 11

heap after 3,1,5   : [1, 3, 5]     smallest = 1
see 12  > 1  → replace 1  : [3, 5, 12]
see 2   < 3  → ignore
see 11  > 3  → replace 3  : [5, 11, 12]     → the 3 largest
```

Python's `heapq` is a min-heap on a list: `heappush`, `heappop`, `heapreplace`, `nsmallest`.

| Function | Does |
|---|---|
| `k_largest(nums, k)` | the k biggest values, biggest first; one pass, O(k) space |
| `k_most_frequent(words, k)` | the k most common words; ties go to the alphabetically smaller word |
| `KthLargest(k, nums)` | `add(val)` returns the current k-th largest of the stream (`None` until k values exist) |

```bash
cd exercises
uv run pytest dsa/stage-4/10-top-k
```
