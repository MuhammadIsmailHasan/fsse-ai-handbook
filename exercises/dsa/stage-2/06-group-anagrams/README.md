# DSA · Stage 2 · Group Anagram Tags

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n · k) where k = word length

Users type skill tags with scrambled letters (`"sql"`, `"lqs"`). Group words that are anagrams of each other.

`group_anagrams(words)` → a list of groups:
- each group keeps words in their **input order** (duplicates stay)
- groups are ordered by the position of their **first** word in the input

```python
group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
# [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
```

Hint: what **key** is identical for all anagrams? (A dict keeps insertion order.)

```bash
cd exercises
uv run pytest dsa/stage-2/06-group-anagrams
```
