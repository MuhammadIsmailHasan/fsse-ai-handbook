---
title: "Backtracking"
summary: "Search every possibility without drowning in them — the choose/explore/un-choose template, subsets, permutations, combinations, duplicate handling, grid walks, N-Queens, and the pruning that turns an impossible search into an instant one."
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 210
tags: [dsa, backtracking, recursion, permutations, subsets, pruning, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The one template behind every backtracking problem: **choose → explore → un-choose**
- Build **subsets**, **permutations** and **combinations** — and know which one a question wants
- Handle **repeated values** without producing the same answer twice
- Walk a **grid** while marking and un-marking cells
- Solve **N-Queens** with O(1) conflict checks
- **Pruning**: why cutting dead branches *is* the algorithm, not an optimization
- 🧭 How to recognize a backtracking question

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Backtracking** | Try one option, and if it fails, take the step back and try the next | Coba-balik |
| **Decision tree** | The imaginary tree of every choice you could make | Pohon keputusan |
| **Path** | The choices you have made so far | Jalur pilihan |
| **State** | What you are tracking right now: used items, sums, marks | Keadaan |
| **Un-choose** | Undoing a choice so the next option starts clean | Membatalkan pilihan |
| **Pruning** | Cutting a branch early because it cannot possibly work | Memotong cabang |
| **Subset** | Any selection; order does not matter | Himpunan bagian |
| **Permutation** | An arrangement; order *does* matter | Permutasi |

## 🧠 The big idea

> Backtracking is **trying on clothes in a shop**.

You take a shirt, put it on, look in the mirror. Not right? You **take it off and put it back on the rack**, then try the next one. You never leave the fitting room wearing five shirts at once, and you never leave a shirt crumpled on the floor — the rack must look exactly as it did, or the next person sees a mess.

That "put it back" is the whole lesson. Recursion walks forward. Backtracking walks forward **and cleans up on the way out**.

```python
def explore(state):
    if state is complete:
        record it
        return
    for each option:
        if option is impossible:
            continue          # ← pruning
        apply option          # ← choose
        explore(state)        # ← explore
        undo option           # ← un-choose
```

Every problem in this lesson is that function with a different `option` and a different `impossible`.

## ❓ Why it matters

Two reasons, and the second one is the bigger one.

**It appears constantly in interviews.** "Generate all…", "find a valid arrangement", "solve this puzzle" — subsets, permutations, combination sum, word search, N-Queens and Sudoku are all one template. Recognizing it means you start writing in the first minute instead of staring.

**And it is the shape of real work:**

| Real job | The search |
|---|---|
| QA test matrix: which combinations of feature flags to test | subsets, minus the combinations that are invalid together |
| A scheduler: assign shifts, rooms, interview slots | one decision per slot, with conflict sets |
| A package manager picking versions that satisfy every dependency | backtracking with pruning (this is literally how `pip` resolves) |
| A regex engine matching `a*b?c` | try, fail, step back, try the next length |
| A form builder validating "these options cannot be chosen together" | prune the branch |

When you say "I'll model it as a search over decisions and prune invalid states", you are describing a dependency resolver, and that is a senior sentence.

## 📖 Step by step

### 1. Subsets: record at every node

For `[1, 2]` every point in the tree is already a valid answer, so you record on the way down.

```text
                []
        ┌───────┴───────┐
      take 1          skip 1
       [1]              []
     ┌──┴──┐          ┌──┴──┐
   [1,2]   [1]       [2]    []
```

```python
def subsets(nums):
    result, path = [], []

    def explore(start):
        result.append(path[:])                 # a copy! see Common mistakes
        for i in range(start, len(nums)):
            path.append(nums[i])               # choose
            explore(i + 1)                     # explore (i + 1: never look back)
            path.pop()                         # un-choose

    explore(0)
    return result
```

`start` is what keeps `[1, 2]` and `[2, 1]` from both appearing: once you have moved past an index you never return to it. There are **2ⁿ** subsets, so this is O(n · 2ⁿ) — the `· n` is the cost of copying each path.

### 2. Permutations: record only at the bottom

Now order matters, so every item may be used at any position — you just cannot use the same item twice.

```python
def permutations(nums):
    result, path = [], []
    used = [False] * len(nums)

    def explore():
        if len(path) == len(nums):
            result.append(path[:])
            return                             # only complete arrangements count
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            explore()
            path.pop()
            used[i] = False

    explore()
    return result
```

**n!** results. `n = 10` is already 3.6 million, so permutations only ever appear with small inputs. If an interviewer gives you `n = 1000` and you reach for permutations, you have misread the question.

| | Record where | Loop over | Count |
|---|---|---|---|
| Subsets | every node | `start … n` | 2ⁿ |
| Permutations | the leaves | all unused | n! |
| Combinations of size k | nodes at depth k | `start … n` | C(n, k) |

### 3. Duplicates: the same answer twice

`[1, 2, 2]` has 8 branches but only **6 distinct** subsets. The fix is always the same: **sort**, then refuse to use an equal value twice *at the same level*.

```python
ordered = sorted(nums)
...
for i in range(start, len(ordered)):
    if i > start and ordered[i] == ordered[i - 1]:
        continue                               # same value, same position → same shape
```

Read `i > start` carefully. It means "I am not the first option at this level". The first `2` is allowed; the second `2` *as a sibling choice* is not. But going **deeper** with another `2` is still fine, which is how `[2, 2]` survives.

For permutations with duplicates the test is different, because position matters:

```python
if i > 0 and ordered[i] == ordered[i - 1] and not used[i - 1]:
    continue                                   # my equal twin before me is not placed yet
```

> Analogy: two identical `2` coins. Deciding *which* identical coin you picked is meaningless, so you fix a rule — always take the left one first. Any arrangement that takes the right one first is the same arrangement, counted twice.

### 4. Grids: mark, walk, un-mark

A grid is a graph whose neighbours are up/down/left/right. Word search is DFS plus one line:

```python
def exists(board, word):
    rows, cols = len(board), len(board[0])

    def walk(row, col, index):
        if index == len(word):
            return True
        if not (0 <= row < rows and 0 <= col < cols) or board[row][col] != word[index]:
            return False
        board[row][col] = "\0"                 # mark: I am standing here
        found = (walk(row + 1, col, index + 1) or walk(row - 1, col, index + 1)
                 or walk(row, col + 1, index + 1) or walk(row, col - 1, index + 1))
        board[row][col] = word[index]          # un-mark on the way out
        return found

    return any(walk(r, c, 0) for r in range(rows) for c in range(cols))
```

Drop that last line and the first failed attempt poisons the board forever: later searches see cells that are not really occupied. Say out loud in an interview: *"I mark the cell, and I restore it on the way out, so the board the caller gave me is unchanged."*

### 5. Pruning: this is the algorithm

Everything above is bookkeeping. **Pruning is where backtracking earns its name.** Compare the two halves of combination sum:

```python
for i in range(start, len(ordered)):
    if ordered[i] > remaining:
        break              # sorted, so every later candidate is too big as well
```

One line, and whole subtrees never get built.

N-Queens shows it best. Place one queen per row, so rows can never clash. For the rest, notice that every cell on a diagonal shares a number:

```text
row + col  (↗)                 row - col  (↘)
  0 1 2 3                        0 -1 -2 -3
  1 2 3 4                        1  0 -1 -2
  2 3 4 5                        2  1  0 -1
  3 4 5 6                        3  2  1  0
```

```python
def count_queen_placements(n):
    columns, rising, falling = set(), set(), set()

    def place(row):
        if row == n:
            return 1
        found = 0
        for col in range(n):
            if col in columns or row + col in rising or row - col in falling:
                continue                       # attacked → dead branch, cost: 3 lookups
            columns.add(col); rising.add(row + col); falling.add(row - col)
            found += place(row + 1)
            columns.remove(col); rising.remove(row + col); falling.remove(row - col)
        return found

    return place(0)
```

Three O(1) set lookups replace scanning the board. That is the difference between `n = 9` answering instantly and not finishing.

Three prunings worth knowing by name:

- **Impossible-state check** — "this violates a rule, stop" (N-Queens, invalid flag combinations).
- **Bound check** — "even in the best case this branch cannot beat what I already have, stop". Keep a best-so-far and compare; this is called *branch and bound*.
- **Order the options** — try the choice with the **fewest remaining possibilities first**, so dead ends appear at the top of the tree where they cost nothing. Sudoku solvers fill the most-constrained cell first for exactly this reason.

:::tip[🧭 How to spot a backtracking question]
- **"Generate all / list every / print all possible"** → subsets, permutations or combinations. Decide which by asking: *does order matter?* and *can items repeat?*
- **"Find **a** valid …" / "is there an arrangement where …"** → backtracking that stops at the first success (`return True`).
- **"How many ways …"** with small `n` → count branches. With large `n` → it is dynamic programming, not this lesson.
- **"Partition / split into groups"** → backtracking with heavy pruning.
- **Puzzle words** — board, grid, queens, sudoku, maze, word — almost always mark/un-mark.
- Input limits are the giveaway: `n ≤ 20` invites 2ⁿ, `n ≤ 10` invites n!. `n ≤ 100000` never does.
:::

### Choosing your setup

| Situation | Use |
|---|---|
| Need every answer | collect into a `result` list |
| Need only one answer | `return True` and unwind immediately |
| Need only the count | return an `int`, never build the lists (saves memory) |
| Need the best answer | keep a best-so-far and prune by bound |
| Values repeat in the input | sort, then skip equal siblings |
| `n` is large (> ~20) | stop — look for DP, greedy or a formula |

- ✅ Small inputs, "all possibilities", constraint puzzles, validity search.
- 🚫 Large inputs where answers overlap — that overlap is what DP exploits (next lesson).
- 🚫 Anything where a greedy rule provably works; backtracking would be slower for the same answer.

## ⚠️ Common mistakes

- `result.append(path)` instead of `result.append(path[:])` — you store the *same list* every time, and because you keep popping from it, every answer ends up empty. The single most common backtracking bug.
- Forgetting to un-choose, so state leaks into the next branch (grids stay marked, `used` stays `True`).
- Mutating the caller's input and not restoring it.
- Duplicate skip with `i > 0` instead of `i > start`, which also kills legitimate deeper repeats like `[2, 2]`.
- Recursing with `i + 1` when the candidate may be reused, or with `i` when it may not.
- Reversing a prerequisite: in permutations-with-duplicates the condition is `not used[i - 1]`, not `used[i - 1]`.
- No pruning at all, then blaming the language for the timeout.
- Hitting Python's recursion limit (~1000 frames) on a deep search — convert to a loop with an explicit stack, or raise the limit knowingly.
- Building every result when the question only asked "how many".

## 🏆 Best practices

- [ ] Write the template first (choose / explore / un-choose), then fill in the three blanks.
- [ ] Say what one "decision" is before coding: a column for this row, an index to take or skip.
- [ ] Append **copies** of the path, never the path itself.
- [ ] Every `choose` has exactly one matching `un-choose`, on every exit path.
- [ ] Leave inputs exactly as you received them.
- [ ] Add pruning as a separate, named step, and say what it saves.
- [ ] State the cost honestly: 2ⁿ, n!, or "exponential but pruned hard".
- [ ] Test the empty input, one item, all-identical items, and a case with no answer at all.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a friend, using the fitting-room analogy, why `result.append(path)` returns a list full of empty lists while `result.append(path[:])` works — and why the bug is invisible for a one-element input.

## 📐 Design it

CareerPilot grows a **mock-interview planner**. You have:

- **6 practice sessions** over two weeks (3 per week)
- a list of **weak topics** (arrays, graphs, system design, …) — no topic twice
- **3 partners**, each with times they cannot do and topics they refuse
- a rule: **no partner twice in the same week**

Design the search that produces a valid plan, reports clearly when none exists, and could later be asked for the *best* plan (partners matched to their strongest topics) instead of just a valid one.

:::quiz
Show a possible design

- **One decision per session.** Sessions are the rows, like N-Queens: session 1 gets a (topic, partner) pair, then session 2, and so on. Never "choose a topic for all sessions at once" — that is a bigger tree for the same answers.
- **State, all O(1) to check:** `used_topics` (a set), `partner_count_this_week` (a dict per week), and the partner's own unavailability tables. Conflict test before choosing: topic unused, partner free at that time, partner accepts the topic, partner not already used this week.
- **The template:** for each candidate pair at this session → if it conflicts, `continue`; else add to the sets, recurse to the next session, then remove from the sets.
- **Stop at the first full plan** (`return True`) because the question asks for *a* valid plan. Collecting all of them would be thousands of near-identical schedules.
- **Pruning that matters:** (1) if the number of unused topics is smaller than the number of remaining sessions, give up immediately; (2) order sessions by **fewest available pairs first** — the Friday slot only one partner can do gets decided at the top of the tree, where failing is cheap.
- **Clear failure:** when the search returns `False`, do not say "no plan". Report the session where every branch died and the reason counts: *"Session 5: all 3 partners unavailable on Friday evening"*. Collect the reasons during the search.
- **Asking for the best plan later** turns this into **branch and bound**: score each pair (partner strength × topic weakness), keep the best complete plan found so far, and prune any branch whose best possible remaining score cannot beat it. Same template, one extra comparison.
- **Cost:** at most (topics × partners)⁶ branches, which pruning cuts to a handful. Tiny — and worth saying out loud, because it justifies backtracking instead of a solver library.

**Rule shown:** one decision per slot, conflicts as sets, fewest-options-first, and a bound if you need the *best* rather than *a* answer.
:::

### 📝 Self-review checklist

- [ ] One decision per session, not per topic
- [ ] Every conflict check is O(1)
- [ ] Choose and un-choose are paired
- [ ] Failure is explained, not just reported
- [ ] The path from "valid" to "best" is one bound check

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s5-subsets-permutations" title="Subsets & Permutations" difficulty="medium" path="exercises/dsa/stage-5/01-subsets-and-permutations"}
The four building blocks: all subsets, distinct subsets with repeated values, all permutations, distinct permutations.
:::

:::problem{id="dsa-s5-combination-sum" title="Combination Sum & Equal Groups" difficulty="medium" path="exercises/dsa/stage-5/02-combination-sum"}
Combinations that hit a target with and without reuse, then split a list into k groups of equal sum — where pruning is the exercise.
:::

:::problem{id="dsa-s5-word-search" title="Word Search & Routes on a Grid" difficulty="medium" path="exercises/dsa/stage-5/03-word-search"}
Spell a word by walking a grid, filter a word list, and count routes that cover every open cell exactly once.
:::

:::problem{id="dsa-s5-n-queens" title="N-Queens" difficulty="hard" path="exercises/dsa/stage-5/04-n-queens"}
Stretch: count all solutions and return one board, with O(1) diagonal checks so n = 9 is instant.
:::

:::hints
- Subsets: `result.append(path[:])` at the **top** of `explore`, before the loop — every node is an answer.
- Subsets keep the input order inside each subset, so loop `for i in range(start, len(nums))` and recurse with `i + 1`.
- Distinct subsets: sort first; inside the loop `if i > start and a[i] == a[i - 1]: continue`.
- Permutations: record only when `len(path) == len(nums)`; keep a `used` list of booleans.
- Distinct permutations: sort, then `if i > 0 and a[i] == a[i - 1] and not used[i - 1]: continue`.
- Combination sum: candidates may be reused, so recurse with `i`, not `i + 1`; sort and `break` when `a[i] > remaining`.
- `combination_sum_once`: recurse with `i + 1` **and** use the same-level duplicate skip.
- Equal groups: return `False` early if `sum(nums) % k`, or if `max(nums) > sum(nums) // k`.
- Equal groups: sort descending, fill one group at a time, skip a group that holds the same amount as one you already tried, and `break` after a failure in an **empty** group.
- Word search: write `board[row][col] = "\0"` before the four recursive calls and restore the letter after them.
- `count_routes`: count the open cells first; a route counts only when you land on `E` having stepped on all of them.
- N-Queens: one queen per row; keep `columns`, `rising = row + col` and `falling = row - col` as sets.
- N-Queens: `first_queen_board` must `return True` up the stack at the first full board, and render rows as `"." * col + "Q" + "." * (n - col - 1)`.
:::

## ✅ Quick check

:::quiz
Why must you append `path[:]` instead of `path`?

`path` is one list that you keep appending to and popping from. Storing it stores a reference, so every stored "answer" points at the same list — and by the time the search finishes, that list is empty again. `path[:]` makes a snapshot of the path as it is right now. The bug hides on single-element inputs, where the path is never popped before the end.
:::

:::quiz
Subsets record at every node of the tree, permutations only at the leaves. Why?

A subset is any selection, so a half-built path like `[1]` is already a complete, valid subset. A permutation must contain every item, so a half-built path is not an answer yet — only a full-length path counts.
:::

:::quiz
Pruning is often called an optimization. Why is that the wrong word for backtracking?

Without pruning the search visits every branch, which for most real inputs never finishes — so there is no slow-but-working version to optimize. The pruning *is* what makes the algorithm run at all. N-Queens at n = 9 and splitting 16 numbers into 4 groups are both impossible without it and instant with it.
:::

## 📚 Keep learning

- [VisuAlgo: N-Queens and recursion trees](https://visualgo.net/en/recursion)
- [Wikipedia: Backtracking](https://en.wikipedia.org/wiki/Backtracking)
- [Python docs: `sys.setrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
