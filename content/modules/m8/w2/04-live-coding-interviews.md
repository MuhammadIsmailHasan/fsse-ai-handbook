---
title: "Live Coding Interviews"
summary: Solve problems while someone watches — a clarify-to-test flow, thinking out loud, DSA patterns under time pressure, getting unstuck with hints, practical API and React rounds, and how to practise.
type: career
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 150
tags: [career, interviews, live-coding, dsa, problem-solving]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What interviewers score in live coding (it's not only "correct answer")
- A repeatable **7-step flow**: clarify → examples → approach → complexity → code → test → improve
- **Thinking out loud** without rambling
- Mapping problems to **patterns** from the DSA track
- Getting **unstuck** and using hints gracefully
- **Practical** rounds: build a small endpoint, fix a bug, write a React component
- A practice plan with timed mocks

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Live coding** | Writing code while an interviewer watches | Menulis kode saat diamati |
| **Rubric** | The list of things they score you on | Daftar penilaian |
| **Clarify** | Asking questions about the problem before coding | Menanyakan detail soal |
| **Think out loud** | Saying what you're considering, as you consider it | Menjelaskan sambil berpikir |
| **Pattern** | A known approach (two pointers, hash map) that fits the problem | Pola penyelesaian |
| **Complexity** | The Big-O of your approach | Kompleksitas |
| **Hint** | Help from the interviewer — accepting it well is a plus | Petunjuk dari pewawancara |
| **Practical round** | Building a small endpoint or component instead of a puzzle | Sesi tugas nyata |

## 🧠 The big idea

Live coding is **cooking on a TV show**. The judges care about the dish, but they also watch how you plan, keep your station clean, taste as you go and recover when something burns. Narrating your cooking lets them give you points even if the soufflé doesn't fully rise.

## ❓ Why it matters

Interviewers can't read your mind, and the score sheet has more rows than "correct answer": how you clarify, how you plan, whether you test, how you react when stuck.

The cooking-show picture explains the whole round: the judges care about the dish, but they also watch how you plan, keep your station clean, taste as you go, and recover when something burns. Narrating gives them something to score even when the soufflé doesn't rise.

For remote interviews there's a practical layer too: a quiet room, a stable connection, and saying "let me share my screen" smoothly all cost you nothing and remove distractions from the actual assessment.

## 📖 Step by step

### 1. What's scored (typical rubric)

| Signal | Looks like |
|---|---|
| Problem understanding | asks clarifying questions, identifies edge cases |
| Problem solving | considers approaches, chooses with reasons |
| Coding | readable names, small functions, correct language use |
| Verification | walks through examples, tests edge cases, fixes bugs calmly |
| Communication | explains thinking, listens to hints |

### 2. The 7-step flow (45-minute round)

Follow it even when you think you know the answer. Jumping straight to code is the most common way strong candidates lose points.

| Step | Minutes | Say |
|---|---|---|
| 1. **Clarify** | 3 | "Can the list be empty? Are values unique? What should I return if nothing matches?" |
| 2. **Examples** | 3 | write 2 normal + 1–2 edge examples with expected outputs |
| 3. **Approach** | 5 | brute force first ("O(n²) by checking all pairs"), then improve ("a hash map gives O(n)") |
| 4. **Complexity** | 1 | time and space of the chosen approach |
| 5. **Code** | 15–20 | narrate intent at each block, not every keystroke |
| 6. **Test** | 5 | trace an example line by line; run edge cases |
| 7. **Improve** | remaining | discuss trade-offs, follow-ups |

### 3. Worked example

> "Given a list of job applications `(company, status)`, return the company with the most interviews. Ties → alphabetically first."

```python
def top_interview_company(applications: list[tuple[str, str]]) -> str | None:
    # Clarified: statuses are lowercase strings; empty input → None; ties → alphabetical.
    counts: dict[str, int] = {}
    for company, status in applications:
        if status == "interview":
            counts[company] = counts.get(company, 0) + 1
    if not counts:
        return None
    # max by (count desc, name asc)
    return min(counts, key=lambda company: (-counts[company], company))


assert top_interview_company([]) is None
assert top_interview_company([("Kopi Data", "applied")]) is None
assert top_interview_company([("B", "interview"), ("A", "interview")]) == "A"
assert top_interview_company([("B", "interview"), ("B", "interview"), ("A", "interview")]) == "B"
```

Narration sample: *"I'll count interviews per company with a dictionary — one pass, O(n). For the tie-break I'll use `min` with a key of negative count, then name, so the highest count wins and names break ties alphabetically."*

### 4. Patterns you already know (DSA track)

| Clue in the problem | Try |
|---|---|
| "pairs that sum to", "seen before", counting | hash map / set |
| sorted array, "find position/first ≥" | binary search |
| contiguous subarray / substring with a condition | sliding window |
| range sums | prefix sums |
| sorted input, pairs from both ends | two pointers |
| matching brackets, "most recent" | stack |
| levels, shortest path in unweighted graph | BFS |
| top K | heap |

### 5. When you're stuck

Say what you know, say what you've ruled out, and ask a specific question. Silence is the only answer that scores nothing.

1. Say it: "I'm stuck on how to handle duplicates; let me try a smaller example."
2. Solve by hand on a tiny input; describe what *you* did — that's the algorithm.
3. Go back to brute force and optimize the slow part.
4. Take hints as collaboration: "That's helpful — so a set would let me check in O(1)…".

### 6. Practical rounds

| Round | Tips |
|---|---|
| **Build an endpoint** (Flask/FastAPI) | clarify input/output and errors; validate input; return proper status codes; write one test |
| **Fix a bug** in unfamiliar code | reproduce first, read error messages, add a failing test, fix minimal, re-run |
| **React component** (e.g. searchable list, tabs, form) | start with static markup, then state, then events; accessibility (labels, buttons); handle empty/loading states |
| **SQL query** | clarify schema, start with `SELECT … FROM … JOIN`, then filters, grouping, ordering; think about indexes |

### 7. Environment and AI

- Practice in the tools they use (CoderPad-like editors, shared IDE, screen share).
- Unless explicitly allowed, **don't use AI assistants or copilots** in live interviews — if allowed, narrate how you verify their output.
- Set up: quiet room, stable internet, zoom-in font size, water.

### Choosing your setup

Every option here is a trade-off:

| Practice method | ✅ | ❌ |
|---|---|---|
| Solving alone on LeetCode-style sites | volume, patterns | no communication practice |
| Timed mock interviews with peers | realistic pressure, feedback | scheduling |
| Explaining solutions in writing/posts | deep understanding | slower |
| Memorizing solutions | fast recall | fails on variations |

## ⚠️ Common mistakes

- Coding before understanding; not asking about edge cases.
- Optimizing prematurely and never finishing.
- Silent struggling; arguing with hints.
- Not testing; declaring victory on the happy path.

## 🏆 Best practices

- [ ] Follow the 7-step flow every time — even for easy problems.
- [ ] Clarify and write examples before coding.
- [ ] State brute force, then optimize; give complexity.
- [ ] Narrate intent; listen for hints.
- [ ] Test with examples and edge cases before saying "done".
- [ ] Practice patterns weekly (DSA track spaced review) and do timed mocks out loud.
- [ ] Prepare practical rounds too: a small API, a bug fix, a React component.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the TV cooking show analogy and why narrating your approach can earn points even when your solution isn't perfect.

## 📐 Design it

For the problem *"Given daily application counts for N days and an integer K, return the maximum number of applications sent in any K consecutive days"*, write your clarifying questions, examples, brute-force and optimized approaches with complexity, and the narration you'd use.

:::quiz
Show a model answer

- **Clarify:** Can K be larger than N? (→ return sum of all or raise? ask) · Are counts non-negative? · Empty list? · Return the sum only, or the start index too?
- **Examples:** `[1, 3, 2, 5, 1], K=2` → `7` (2+5) · `[4], K=1` → `4` · `[], K=1` → `0` (agreed)
- **Brute force:** sum every window of K → O(N·K) time, O(1) space.
- **Optimized:** sliding window — sum the first K, then add the new day and subtract the day leaving → O(N) time, O(1) space.
- **Narration:** "Windows overlap, so recomputing each sum wastes work. I'll keep a running sum: when the window moves right by one, add the entering day and subtract the leaving day, and track the maximum."
- **Tests:** K = N, K = 1, all zeros, K > N per the clarified rule.
:::

### 📝 Self-review checklist

- [ ] Clarifying questions cover edge cases
- [ ] Complexity stated for both approaches
- [ ] Tests planned before "done"

::ai-review{task="explain"}

::part[Practice]{n="3"}

## 🛠️ Do it

1. Do 3 timed (45 min) problems **out loud**, recording the screen and voice; review the recordings with the rubric.
2. Do one practical round: build `GET /jobs?q=` with validation and a test in 45 minutes.
3. Do one mock with a peer on a shared editor; swap interviewer/candidate.

## ✅ Done when

- [ ] 3 recorded solo mocks reviewed with the rubric
- [ ] 1 practical round completed
- [ ] 1 peer mock done; top 2 improvements written down

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Live coding | Menulis kode secara langsung saat wawancara |
| Clarifying question | Pertanyaan klarifikasi |
| Edge case | Kasus batas/tepi |
| Brute force | Solusi coba semua kemungkinan |
| Time complexity | Kompleksitas waktu |
