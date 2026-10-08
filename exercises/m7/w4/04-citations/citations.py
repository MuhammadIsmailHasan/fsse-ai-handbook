"""Module 7 · W4 — Citations you can check (no API key needed).

A cited answer lets a person verify it. But a model can write [3] when there is no source 3, or put a
quote in quotation marks that is not in the source. Checking citations is cheap code, not a model job.
"""

import re  # noqa: F401


def extract_citations(answer: str) -> list[int]:
    """The source numbers cited in the answer, in order of FIRST appearance, without repeats.
    A citation is a number in square brackets: [1], [12]. A bracket with several numbers, [1, 3] or [1,3], cites each.
    Ignore brackets with other content, like [note] or [1a]. Example: "A [2]. B [1, 2]. C [3]." -> [2, 1, 3]"""
    raise NotImplementedError


def validate_citations(answer: str, source_count: int) -> list[str]:
    """Problems in an answer that is supposed to use source_count numbered sources. Return messages in this order:
      "unknown source [N]"        for each cited number outside 1..source_count (in order of first appearance)
      "no citations"              if the answer cites nothing, has at least one sentence, and source_count > 0
      "uncited sentence: <text>"  for each sentence (split like: after . ! ? followed by space) that has no [n] in it,
                                  EXCEPT sentences that start with "I do not know", "I don't know" or "I could not find"
    Do not report "uncited sentence" when "no citations" was reported. Empty list = fine."""
    raise NotImplementedError


def normalize(text: str) -> str:
    """Lowercase, replace every run of whitespace by one space, strip, and remove these quote marks: " ' “ ” ‘ ’"""
    raise NotImplementedError


def quote_supported(quote: str, source_text: str) -> bool:
    """Is the quote really in the source? Compare normalize(quote) with normalize(source_text) as a substring.
    An empty quote (after normalising) is NOT supported."""
    raise NotImplementedError


def find_fake_quotes(answer: str, sources: list[str]) -> list[str]:
    """Quotes the model wrote that appear in NO source. A quote is the text inside straight double quotes "..."
    of at least 3 words (after normalising). Check each against every source; return the unsupported ones in order of appearance."""
    raise NotImplementedError


def render_sources(answer: str, sources: list[dict]) -> str:
    """Append a source list for the sources that were really cited.
    sources: [{"title": "Refund policy", "url": "https://..."}, ...]   (source 1 is sources[0])
    Result: the answer, then a blank line, then "Sources:" and one line per cited source (in citation order of first appearance):
        [2] Refund policy - https://...
    Cited numbers that do not exist are skipped. If nothing valid is cited, return the answer unchanged."""
    raise NotImplementedError
