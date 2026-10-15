# DSA · Stage 5 · Word Search & Routes on a Grid

> 🟡 Medium · 🚫🤖 No-AI · Target: O(rows · cols · 4^len(word))

A grid is just a graph whose neighbours are up, down, left and right. DFS alone explores it; **backtracking** explores it *and takes the mark back*, so a cell blocked for one attempt is free again for the next.

```text
walk(cell, index):
    off the grid, or wrong letter   -> False
    whole word matched              -> True
    mark cell                       ← "I am standing here"
    try the four neighbours
    un-mark cell                    ← the line people forget
```

Forget the un-mark and the first failed attempt poisons the board forever: later searches see cells that are not really occupied.

| Function | Does |
|---|---|
| `exists(board, word)` | can the word be walked out of the grid? |
| `find_words(board, words)` | which of these words are in there — sorted, no repeats |
| `count_routes(grid)` | routes from `S` to `E` that step on **every** open cell exactly once |

`count_routes` is a *Hamiltonian path* count: there is no clever algorithm, only a careful search. That is the point — interviewers use it to watch whether your state goes back to normal on the way out.

Leave the board exactly as you found it. A test checks this.

```bash
cd exercises
uv run pytest dsa/stage-5/03-word-search
```
