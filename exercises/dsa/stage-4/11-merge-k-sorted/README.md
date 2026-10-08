# DSA · Stage 4 · Merge Sorted Inputs with a Heap

> 🟡 Medium · 🚫🤖 No-AI · Target: O(N log k)

Three sorted lists, one sorted result. You do not need to sort again. Put the **front item of each list** in a heap; the smallest one is the next output. When you take it out, push the next item **from the same list**.

```text
lists: [1, 4, 5]  [1, 3, 4]  [2, 6]

heap  : (1, list 0) (1, list 1) (2, list 2)   → output 1, push list 0's next (4)
heap  : (1, list 1) (2, list 2) (4, list 0)   → output 1, push list 1's next (3)
...
```

| Function | Does |
|---|---|
| `merge_k_sorted(lists)` | k sorted lists → one sorted list, O(N log k) |
| `merge_streams(streams)` | the same, but **lazy**: a generator that also works on infinite streams and never reads ahead |
| `smallest_pair_sums(a, b, k)` | the k smallest `a[i] + b[j]`, without building all the pairs |

Tip: heap entries are tuples like `(value, list_index, position)`. Tuples compare left to right, and the index keeps two equal values from forcing Python to compare something that cannot be compared.

```bash
cd exercises
uv run pytest dsa/stage-4/11-merge-k-sorted
```
