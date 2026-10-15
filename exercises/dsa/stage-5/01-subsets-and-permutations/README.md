# DSA · Stage 5 · Subsets & Permutations

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n · 2ⁿ) for subsets, O(n · n!) for permutations

Backtracking always has the same three lines: **choose → explore → un-choose**. Build one path step by step, record it when it is complete, then take the last step back and try the next option.

```text
subsets([1, 2]):            start []
                        ┌─── take 1 ───┐        ┌── skip 1 ──┐
                       [1]                     []
                   ┌── take 2 ──┐          ┌── take 2 ──┐
                 [1, 2]        [1]        [2]          []
```

Every node of that tree is a valid subset, so you record **at every node**. For permutations you only record at the **bottom**, where the path is full.

| Function | Does | Watch out for |
|---|---|---|
| `subsets(nums)` | all 2ⁿ subsets | append a **copy**: `path[:]` |
| `subsets_no_duplicates(nums)` | distinct subsets when values repeat | sort, then skip an equal value at the same level |
| `permutations(nums)` | all n! orders | track which indexes are already used |
| `permutations_no_duplicates(nums)` | distinct orders when values repeat | skip an equal twin whose predecessor is unused |

The order of the outer list does not matter — the tests compare contents, not order.

```bash
cd exercises
uv run pytest dsa/stage-5/01-subsets-and-permutations
```
