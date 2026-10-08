import re

_BRACKET = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def extract_citations(answer):
    seen, out = set(), []
    for match in _BRACKET.finditer(answer):
        for number in re.split(r"\s*,\s*", match.group(1)):
            n = int(number)
            if n not in seen:
                seen.add(n)
                out.append(n)
    return out


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def validate_citations(answer, source_count):
    problems = []
    cited = extract_citations(answer)
    for n in cited:
        if not 1 <= n <= source_count:
            problems.append(f"unknown source [{n}]")
    sentences = _sentences(answer)
    if not cited:
        if sentences and source_count > 0:
            problems.append("no citations")
        return problems
    for sentence in sentences:
        if sentence.startswith(("I do not know", "I don't know", "I could not find")):
            continue
        if not _BRACKET.search(sentence):
            problems.append(f"uncited sentence: {sentence}")
    return problems


def normalize(text):
    text = re.sub(r"[\"'“”‘’]", "", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def quote_supported(quote, source_text):
    q = normalize(quote)
    return bool(q) and q in normalize(source_text)


def find_fake_quotes(answer, sources):
    fake = []
    for quote in re.findall(r'"([^"]+)"', answer):
        if len(normalize(quote).split()) < 3:
            continue
        if not any(quote_supported(quote, s) for s in sources):
            fake.append(quote)
    return fake


def render_sources(answer, sources):
    lines = []
    for n in extract_citations(answer):
        if 1 <= n <= len(sources):
            s = sources[n - 1]
            lines.append(f"[{n}] {s['title']} - {s['url']}")
    if not lines:
        return answer
    return answer + "\n\nSources:\n" + "\n".join(lines)
