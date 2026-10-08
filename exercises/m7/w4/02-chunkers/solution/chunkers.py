import re

_HEADING = re.compile(r"^(#{1,6}) (.*)$")


def _pieces(paragraphs, max_words):
    pieces, current, count = [], [], 0
    for para in paragraphs:
        words = para.split()
        if len(words) > max_words:
            if current:
                pieces.append(current)
                current, count = [], 0
            for i in range(0, len(words), max_words):
                pieces.append([" ".join(words[i : i + max_words])])
            continue
        if current and count + len(words) > max_words:
            pieces.append(current)
            current, count = [], 0
        current.append(para)
        count += len(words)
    if current:
        pieces.append(current)
    return pieces


def split_markdown(text, max_words):
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    sections, path, body = [], [], []
    current_path = ""

    def flush():
        if "".join(body).strip():
            sections.append((current_path, "\n".join(body)))

    for line in text.split("\n"):
        m = _HEADING.match(line)
        if m:
            flush()
            body = []
            level = len(m.group(1))
            path = path[: level - 1] + [m.group(2).strip()]
            current_path = " > ".join(path)
        else:
            body.append(line)
    flush()
    chunks = []
    for section_path, body_text in sections:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body_text) if p.strip()]
        for piece in _pieces(paragraphs, max_words):
            chunks.append({"path": section_path, "text": "\n\n".join(piece), "index": len(chunks)})
    return chunks


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])(?!\d)\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def sentence_chunks(text, max_words, overlap_sentences=0):
    sentences = split_sentences(text)
    chunks, current = [], []

    def words(sents):
        return sum(len(s.split()) for s in sents)

    for sentence in sentences:
        n = len(sentence.split())
        if current and words(current) + n > max_words:
            chunks.append(" ".join(current))
            carry = current[-overlap_sentences:] if overlap_sentences else []
            current = carry if carry and words(carry) + n <= max_words else []
        current.append(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks


def parent_child(parents, child_words):
    children, parent_of = [], {}
    for parent in parents:
        words = parent["text"].split()
        for n, start in enumerate(range(0, len(words), child_words)):
            child_id = f"{parent['id']}#{n}"
            children.append({"id": child_id, "text": " ".join(words[start : start + child_words])})
            parent_of[child_id] = parent["id"]
    return children, parent_of


def expand_to_parents(hit_ids, parent_of, parents):
    out, seen = [], set()
    for hit in hit_ids:
        pid = parent_of.get(hit)
        if pid is None or pid in seen:
            continue
        seen.add(pid)
        out.append({"id": pid, "text": parents[pid]})
    return out
