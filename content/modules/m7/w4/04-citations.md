---
title: "Citations"
summary: "Make RAG answers checkable — numbered sources, the provider's built-in citation feature, validating citation numbers and quotes in code, showing a clean source list, and knowing what a citation check can and cannot prove."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [rag, citations, grounding, validation, trust]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why **citations** build trust and make errors visible
- Two ways to get them: **your own numbered sources** and the **provider's citation feature**
- How to **validate** citations in code: unknown numbers, uncited sentences, fake quotes
- How to **show sources** clearly to users
- What citations **prove**, and what they do not

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Citation** | A pointer from a claim to the source that supports it | Kutipan sumber |
| **Source number** | The `[1]`, `[2]` label of a source in the prompt | Nomor sumber |
| **Grounded answer** | An answer whose claims are supported by the sources given | Jawaban berpijak |
| **Quote** | Exact words copied from a source | Kutipan langsung |
| **Fake citation** | A citation to a source that does not exist, or does not say that | Kutipan palsu |
| **Cited text** | The exact passage a provider says supports a claim | Teks yang dikutip |
| **Faithfulness** | How well the answer sticks to the sources | Kesetiaan pada sumber |
| **Attribution** | Giving credit and a link to where information came from | Atribusi |

## 🧠 The big idea

A citation is like a **footnote in a research paper**. A claim without a footnote is "trust me". A claim with a footnote is "check me". Readers (and your own team) can follow the footnote, see the source, and decide.

But footnotes can be wrong. A careless student can write "[7]" when there are only three books, cite a book that says the opposite, or put quotation marks around words nobody wrote. So a good system does what a good teacher does: it **checks the footnotes**.

## ❓ Why it matters

- **Trust.** Users believe an answer more, correctly, when they can click the source.
- **Debugging.** When an answer is wrong, the citation shows which chunk misled the model, or that there was none.
- **Safety and law.** In support, health, finance or legal settings you need to show where an answer came from.
- **Detecting hallucination.** An answer that cites nothing, or cites something that does not exist, is a red flag you can catch automatically.

And it is cheap: most of the checking is plain string handling, no extra model call.

## 📖 Step by step

### 1. Make your own citations: numbered sources

You already built this in the architecture lesson: put sources in the prompt with numbers, and tell the model to cite them.

```text
Answer the question using ONLY the sources below. Cite them like [1], [2].
If the sources do not contain the answer, say you do not know.

<sources>
[1] (refund.md)
Refunds are paid back in 7 days after we receive the item.

[2] (shipping.md)
Shipping is free for orders above Rp 200.000.
</sources>

Question: How long does a refund take?
```

A good answer: `Refunds are paid back in 7 days after we receive the item [1].`

Keep a table that maps `[n]` to the real chunk (id, title, URL, page). The number in the text must always map back to something you can show.

### 2. Use the provider's citation feature (when available)

Some model APIs can produce citations for you. You send your documents as special **document blocks** with citations enabled, and the response comes back split into text pieces, each with the exact passages that support it:

```python
response = client.messages.create(
    model=settings.llm_model,
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "text", "media_type": "text/plain", "data": REFUND_POLICY_TEXT},
                "title": "Refund policy",
                "citations": {"enabled": True},          # turn on citations for this document
            },
            {"type": "text", "text": "How long does a refund take?"},
        ],
    }],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
        for citation in getattr(block, "citations", None) or []:
            print("  from:", citation.document_title, "|", citation.cited_text)
```

What you get: `cited_text` (the exact words), `document_index` and `document_title` (which document), and a **location** (character range for plain text, page range for PDFs). Nice properties: the cited text is **guaranteed to come from the document you sent**, so quotes cannot be invented, and you do not have to ask the model to format `[n]` markers.

Things to know (check your provider's current docs):

- citations are enabled **per document**, for all or none of your documents in a request,
- it can conflict with other features, such as forcing a strict JSON output format,
- you pay for the document tokens like any input,
- your own check for "does the claim match the passage" still matters.

Your own numbered-source approach works with any model and any provider. The built-in feature is a good option when it is available.

### 3. Validate the numbers

Never trust that `[n]` is valid. Check it in code:

```python
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
    return out                               # source numbers in order of first use
```

```python
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
            continue                          # an honest refusal does not need a source
        if not _BRACKET.search(sentence):
            problems.append(f"uncited sentence: {sentence}")
    return problems
```

Three problems it catches: a **number that does not exist**, an answer with **no citations at all**, and **sentences with no citation**. When it finds a problem you can retry once ("every claim needs a citation"), show a warning, or fall back to "I could not find this".

Be careful with strictness: not every sentence needs a source (greetings, "Here is what I found:"). Decide the rule for your product and test it.

### 4. Validate the quotes

Models sometimes put words in quotation marks that are not in the source. Check quotes against the sources, ignoring case, spacing and quote marks:

```python
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
            continue                          # very short quoted words are not claims
        if not any(quote_supported(quote, s) for s in sources):
            fake.append(quote)
    return fake
```

If a quote is in no source, either remove the quotation marks (it is a paraphrase), regenerate, or flag the answer.

### 5. Show the sources to the user

A good display shows only the sources that were **really cited**, in the order they appear, with a title and a link:

```python
def render_sources(answer, sources):
    lines = []
    for n in extract_citations(answer):
        if 1 <= n <= len(sources):
            s = sources[n - 1]
            lines.append(f"[{n}] {s['title']} - {s['url']}")
    if not lines:
        return answer
    return answer + "\n\nSources:\n" + "\n".join(lines)
```

Design tips:

- Make `[1]` a **clickable** marker that opens the source, scrolled to the cited passage if you can.
- Show the **title and date**, so users can judge freshness.
- Show the **quote** (`cited_text`) on hover or in a panel, for fast checking.
- Do not list sources that were retrieved but not cited as if they supported the answer.
- Keep the user's permissions in mind: only link to documents they may open.

### 6. What a citation check proves, and what it does not

| Your code can check | Your code cannot fully check |
|---|---|
| the cited number exists | whether the source **really supports** the claim |
| every sentence has a citation | whether the claim is **complete** or missing an exception |
| quoted words appear in a source | whether the source is **correct and current** |
| the source was in the prompt | whether the model **combined** two sources wrongly |

For the right-hand column you use a **judge**: a human review of a sample, or a second model that gets the claim and the cited passage and answers "supported / not supported / partly" (week 5 covers this carefully). Sample and measure it; do not run it blindly on everything.

Also log failures: answers with invalid citations are valuable test cases.

### Choosing your setup

| Situation | Do this |
|---|---|
| Any provider, full control | your own numbered `[n]` sources + validation in code |
| Provider offers document citations | try the built-in feature; still validate and display sources |
| Answers must quote exactly | check quotes against the sources |
| High-risk domain | add a judge step and human review of samples |
| User-facing display | clickable markers, title, date, quote on hover |
| An honest "I do not know" | allow it without a citation |

- ✅ Keep a map from `[n]` to the real chunk.
- ✅ Validate numbers, uncited claims and quotes in code.
- 🚫 Listing every retrieved document as a "source".
- 🚫 Treating a citation as proof that the claim is true.

## ⚠️ Common mistakes

- Trusting `[n]` without checking it exists.
- Showing retrieved documents that the answer never used.
- Numbering sources differently in the prompt and in the UI.
- Letting the model invent a URL or a title: always render these from your own data.
- Requiring a citation on every sentence, including greetings.
- Forgetting to escape the model's text before putting it in HTML.
- Believing a correct-looking citation means a correct claim.
- Not logging invalid citations.

:::revoshop
Write the answer a RevoShop assistant should give to "can I return a worn shoe?" using two sources (a returns policy and a hygiene rule). Add the citation markers, list what your validator would check (numbers, uncited sentences, quotes), and say what the validator cannot catch.
:::

## 🏆 Best practices

- [ ] Number sources in the prompt and keep a map back to chunk id, title, URL and page.
- [ ] Render source titles and links from your own data, never from model text.
- [ ] Validate citation numbers, uncited sentences and quoted text in code.
- [ ] Allow honest refusals without citations.
- [ ] Display only really cited sources, with clickable markers and the quoted passage.
- [ ] Use a judge (human sample or model) to check that sources support claims.
- [ ] Log and review answers with invalid or missing citations.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain citations with the footnote picture. Why is "the citation exists" different from "the claim is true"?

## 📐 Design it

SupportDesk AI's answers to customers must include sources. Last week a customer got "Refunds take 3 days [4]" but the prompt only had three sources, and the real policy says 7 days. Design the validation, the display, the failure handling, and the monitoring so this cannot reach a customer again.

:::quiz
Show a possible design

- **Validation in code before sending:** `extract_citations` finds `[4]`; `validate_citations(answer, 3)` reports `unknown source [4]`. Also check uncited sentences and quotes against the three sources.
- **Failure handling:** on any problem, retry once with the model told what was wrong ("source 4 does not exist; cite only sources 1–3"), re-validate; if it still fails, return the safe message ("I could not verify this; here are the related articles" with the links) and hand off to a human if the customer asks.
- **Support-claim check:** for numbers (days, prices) extract the number from the answer and confirm the same number appears in the cited source chunk (a cheap guard against "3 days" vs "7 days"). For high-risk topics, add a small judge call ("does this passage support this sentence?").
- **Display:** only the really cited sources, rendered from your database with title, last updated date and link; markers open the passage.
- **Prompt:** numbered sources, "cite like [1]", "only cite numbers that appear", and "if the sources do not contain the answer, say you do not know".
- **Monitoring:** log every validation failure with the question, retrieved ids and answer; track the share of answers with invalid citations (alert above 1%); add each failure to the test set.
- **Evaluation:** a set of questions whose correct numbers are known; measure how often the answer has the right number *and* a valid citation.
- **Root cause:** also look at retrieval: the right policy chunk (7 days) may have been missing from the prompt, which is why the model invented a number.

**Rule shown:** let code check everything it can (numbers, uncited claims, quotes, figures), and use a judge for the rest.
:::

### 📝 Self-review checklist

- [ ] Citation numbers are validated against the real source count
- [ ] Source titles and links come from your data
- [ ] There is a fallback when validation fails
- [ ] Failures are logged and become test cases

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w4/04-citations" ai="no-ai" title="Citations you can check"}
Write `extract_citations` (including `[1, 3]`), `validate_citations` (unknown numbers, no citations, uncited sentences, honest refusals allowed), `normalize`, `quote_supported`, `find_fake_quotes` (quotes of at least 3 words found in no source) and `render_sources` (only really cited sources, in order). No API key needed.
:::

:::hints
- Regex for brackets: `\[(\d+(?:\s*,\s*\d+)*)\]`; split the inside on commas.
- Keep first-appearance order with a `seen` set.
- `validate_citations`: do not report "uncited sentence" when "no citations" was already reported.
- Sentences: `re.split(r"(?<=[.!?])\s+", text.strip())`; skip refusals that start with "I do not know", "I don't know" or "I could not find".
- `normalize`: lowercase, remove quote marks, collapse whitespace, strip.
- `render_sources`: skip numbers outside `1..len(sources)`; if no valid line, return the answer unchanged.
:::

## ✅ Quick check

:::quiz
The answer cites [5] but only 3 sources were in the prompt. What do you do?

Treat it as an invalid answer: do not show it as is. Retry once with a correction telling the model to cite only the sources it was given, and if it still fails, show a safe fallback. Log the failure as a test case.
:::

:::quiz
A citation check passes. Is the answer correct?

Not necessarily. The check proves the numbers and quotes are consistent with the sources, not that the source really supports the claim, is complete, or is up to date. Use a judge (human sample or model) and good retrieval for that.
:::

:::quiz
Why render source titles and URLs from your own data instead of using the model's text?

The model can invent a plausible title or link. If your code looks up the cited number in its own table of sources, the user only ever sees real, permitted documents.
:::

## 📚 Keep learning

- [Anthropic docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- [Anthropic docs: Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- [Gao et al.: Enabling LLMs to Generate Text with Citations (paper)](https://arxiv.org/abs/2305.14627)
