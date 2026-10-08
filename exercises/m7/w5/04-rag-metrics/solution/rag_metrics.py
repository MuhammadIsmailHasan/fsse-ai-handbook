import re

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "to", "of", "in", "on", "at", "for", "and", "or",
    "it", "its", "this", "that", "with", "as", "by", "from", "we", "you", "your", "our", "can", "will", "after",
}


def split_claims(answer):
    text = re.sub(r"\s*\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", answer)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def content_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def claim_supported(claim, contexts, threshold=0.8):
    words = content_words(claim)
    if not words:
        return True
    available = set()
    for context in contexts:
        available |= content_words(context)
    return len(words & available) / len(words) >= threshold


def faithfulness(answer, contexts, threshold=0.8):
    claims = split_claims(answer)
    if not claims:
        return 1.0
    return sum(claim_supported(c, contexts, threshold) for c in claims) / len(claims)


def context_precision(relevance_flags):
    total, relevant_so_far = 0.0, 0
    for k, flag in enumerate(relevance_flags, start=1):
        if flag:
            relevant_so_far += 1
            total += relevant_so_far / k
    return total / relevant_so_far if relevant_so_far else 0.0


def _share(facts, text):
    if not facts:
        return 1.0
    lowered = text.lower()
    return sum(f.lower() in lowered for f in facts) / len(facts)


def context_recall(required_facts, contexts):
    return _share(required_facts, " ".join(contexts))


def answer_coverage(required_facts, answer):
    return _share(required_facts, answer)
