# Example: Word Count

> 🚫🤖 **No-AI** · ⏱️ ~15 min

This sample exercise shows how every exercise in the handbook is organised.

## Task

Implement `count_words(text)` in `word_count.py`. It returns a dictionary that maps each word to how many times it appears.

Rules:
- Words are separated by whitespace.
- Counting ignores upper/lower case: `"Hi hi"` → `{"hi": 2}`.
- An empty string returns an empty dictionary.

## Run the checks

```bash
cd exercises
uv run pytest _example/01-word-count
```

## Stretch goal 🏆

Add `top_words(text, n)` that returns the `n` most common words as a list of `(word, count)` tuples, most common first.
