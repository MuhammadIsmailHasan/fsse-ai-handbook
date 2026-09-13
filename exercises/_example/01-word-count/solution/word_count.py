"""Reference solution. Compare AFTER you have tried it yourself."""


def count_words(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    # str.split() with no argument splits on ANY whitespace and ignores extra spaces.
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts
