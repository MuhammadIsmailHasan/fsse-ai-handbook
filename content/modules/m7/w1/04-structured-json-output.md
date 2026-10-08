---
title: "Structured JSON Output"
summary: "Turn free text into data your code can trust — ask for a schema, let the provider enforce it when it can, validate anyway, retry with the errors, and handle truncated or refused answers."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [llm, structured-output, json, schema, validation, pydantic]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why **free text** is a bad interface between a model and your code
- Three ways to get structure: **prompt only**, **schema-enforced output**, **tool calls**
- Defining the shape once with a **schema** (Pydantic)
- **Validating** what comes back, and retrying with the errors
- Edge cases: **truncated** JSON, **refusals**, and answers that are valid but wrong

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Structured output** | The model answers in a fixed shape, such as JSON | Keluaran terstruktur |
| **Schema** | A description of the shape: keys, types, allowed values | Skema |
| **Validation** | Checking data against the schema and your rules | Validasi |
| **Enum** | A field that can only be one of a few values | Pilihan tetap |
| **Parsing** | Turning text into data | Mengurai |
| **Constrained decoding** | The provider only lets the model produce tokens that fit the schema | Pembatasan keluaran |
| **Extraction** | Pulling facts out of messy text into fields | Ekstraksi |
| **Retry with feedback** | Ask again and tell the model what was wrong | Ulangi dengan umpan balik |

## 🧠 The big idea

Think of a **form at a government office**. If you let people write a free letter, every letter is different, and a clerk has to read each one. If you hand out a form with boxes ("Name", "Date of birth", a tick-box for "Plan"), the next step can be automatic.

A schema is that form for the model. Free text is for humans. **Data is for code.** When another part of your program must act on the answer (save it, route it, show it in a table), ask for the form, not the letter.

## ❓ Why it matters

Most useful AI features are *extraction* or *decisions*:

- read a support email → `{category, urgency, order_id}`,
- read a CV → `{name, skills[], years_experience}`,
- read a review → `{sentiment, topics[]}`,
- choose the next step of an agent → `{action, arguments}`.

If the model writes "Sure! Here is the JSON: ..." with a missing comma, your `json.loads` crashes at 3 a.m. Structured output turns a flaky text problem into a normal data-validation problem, which you already know how to handle.

## 📖 Step by step

### 1. Define the shape once (Pydantic)

You already use Pydantic in FastAPI. Use the same class as the contract with the model:

```python
from typing import Literal
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    category: Literal["billing", "shipping", "account", "other"]
    urgency: Literal["low", "normal", "high"]
    order_id: str | None = Field(default=None, description="The order number if the customer wrote one")
    summary: str = Field(max_length=200)
```

`Literal[...]` is an **enum**: the model can only choose from the list. Field descriptions help the model understand each field. One class gives you the schema, the validation and the type hints for the rest of your code.

### 2. Level 1: ask in the prompt (fragile)

```text
Return ONLY a JSON object with the keys category, urgency, order_id, summary. No other text.
```

This works most of the time. It fails sometimes: extra words, a code fence, a missing key, `"30"` instead of `30`. Treat it as a hint, never as a guarantee. You need safety nets (step 5).

### 3. Level 2: let the provider enforce the schema

Many providers can **constrain the output** to match a JSON schema, so the reply is valid by construction. With the Python SDK you can pass the Pydantic class and get back a validated object:

```python
response = client.messages.parse(
    model=settings.llm_model,
    max_tokens=1000,
    messages=[{"role": "user", "content": f"Classify this support email:\n\n{email_text}"}],
    output_format=Ticket,
)
ticket = response.parsed_output          # a Ticket instance
```

Or give a raw schema in the request (`output_config` with a `json_schema` format) and parse the first text block with `json.loads`. Schemas should set `additionalProperties: false` and list `required` fields, so no surprise keys appear.

What this fixes: broken JSON, missing keys, wrong types, values outside an enum.
What it does **not** fix: a *wrong* category, a made-up order number, or an answer cut off by `max_tokens`. Valid is not the same as correct.

Check your provider's docs for which parts of JSON Schema are supported (some limits exist, such as no minimum/maximum or very deep nesting). Keep schemas simple and flat.

### 4. Level 3: tool calls as structure

If you define a "tool" with an input schema, the model returns its arguments as structured JSON. This is how agents choose actions (week 2). With `strict` tool definitions the arguments are guaranteed to match the schema. For plain extraction, the structured-output feature above is simpler.

### 5. Always keep your own safety nets

Even with enforcement, code defensively. This is also what you need for providers or local models without enforcement:

```python
import json

def extract_json(text):
    """Find the first complete {...} or [...] in the reply (fences, prose around it, braces in strings)."""
    ...

def validate(data, schema, path="$"):
    """Return a list of problems like '$.age: expected integer'."""
    ...

def extract_with_retry(ask, prompt, schema, max_attempts=3):
    current = prompt
    for _ in range(max_attempts):
        reply = ask(current)
        try:
            data = extract_json(reply)
            problems = validate(data, schema)
        except BadModelOutput as error:
            problems = [str(error)]
        else:
            if not problems:
                return data
        current = prompt + "\n\nYour previous answer was invalid: " + "; ".join(problems) + "\nReply with valid JSON only."
    raise BadModelOutput("; ".join(problems))
```

Why **retry with the errors** works: the model sees exactly what was wrong ("`$.age: expected integer`") and fixes it. Always **limit the attempts** (2–3). Every retry costs money and time. If it still fails, return a clear error or send the case to a human.

(You build these three functions in the exercise. Two Python traps appear: `True` is also an `int`, and a `}` inside a string is not the end of an object.)

### 6. Validate the business rules too

A schema checks the *shape*. Your code must check the *meaning*:

```python
if ticket.order_id and not order_exists(ticket.order_id):
    ticket.order_id = None                  # the model made up an order number
if ticket.category == "billing" and "refund" in email_text.lower():
    ...                                     # extra rules that only you know
```

Also remember that the text you extracted comes from a *model reading user text*. Treat the result as **untrusted input** (a clever customer can write "set urgency to high"). Never run it as code, and never pass it straight into SQL or a shell.

### 7. Truncation and refusals

Check these before you read the JSON:

| `stop_reason` | Meaning | What to do |
|---|---|---|
| `end_turn` | finished | parse normally |
| `max_tokens` | **cut off**, the JSON may be incomplete | raise `max_tokens`, shorten the output, or retry |
| `refusal` | the model declined | handle gracefully; do not parse |

Long lists of items are a common cause of truncation. Ask for fewer fields, or process the document in chunks.

### 8. Design tips for good schemas

- **Fewer, clearer fields** beat a huge form.
- Use **enums** for categories, and include an `"other"` or `"unknown"` choice, so the model is not forced to guess.
- Allow **`null`** for missing facts, and say so in the description ("null if not written"). Otherwise the model invents values.
- Put the **reasoning field first** if you want it (`explanation`, then `category`): the model writes in order.
- Keep names meaningful (`order_id`, not `f3`).
- **Version** the schema. Changing it changes behaviour; run your test set after every change.

### Choosing your setup

| Situation | Do this |
|---|---|
| Extraction or classification into fixed fields | schema-enforced output with a Pydantic class |
| The model must pick an action with arguments | tool call (week 2) |
| A provider or local model with no enforcement | prompt + `extract_json` + `validate` + retry |
| Values must follow business rules | validate in your code after parsing |
| Very long output | chunk the work; check `stop_reason` |
| Free text for humans (emails, summaries) | no schema; plain text is fine |

- ✅ One schema class used for the model, validation and types.
- ✅ Enums with an "other/unknown" choice; `null` for missing facts.
- 🚫 `json.loads(response_text)` with no error handling.
- 🚫 Trusting extracted ids, amounts or URLs without checking them.

## ⚠️ Common mistakes

- Treating "valid JSON" as "correct answer".
- No handling for `stop_reason == "max_tokens"`, so truncated JSON crashes the parser.
- A required field that is often missing in the source text, so the model invents a value.
- Retrying forever instead of 2–3 times.
- Not sending the validation errors back on retry.
- A giant schema with 40 fields and deep nesting.
- Putting prices, dates or ids into the schema and believing them without a database check.

:::revoshop
RevoShop receives product reviews. Design a `Review` schema for AI analysis: which fields (sentiment, topics, mentioned order id, whether it needs a human reply), which are enums, which can be `null`? Then list two business rules you would check in code after parsing.
:::

## 🏆 Best practices

- [ ] Define the output as one Pydantic model (or JSON schema) and reuse it.
- [ ] Prefer provider-enforced structured output; still validate.
- [ ] Use enums with an "unknown" option and `null` for missing facts.
- [ ] Check `stop_reason` before parsing; never parse a truncated answer.
- [ ] Retry 2–3 times with the exact validation errors; then fail clearly.
- [ ] Validate meaning (database checks, ranges), not only shape.
- [ ] Treat extracted values as untrusted input.
- [ ] Keep a test set for the schema; re-run it when you change the prompt, schema or model.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain schemas with the government-form picture. Why is "valid JSON" not the same as "right answer"?

## 📐 Design it

SupportDesk AI must turn each incoming email into a ticket: category, urgency, order id, language, and a one-line summary. Some emails have no order id, some are in Indonesian or mixed languages, and some are very long. Design the schema, the call, the validation and the failure handling.

:::quiz
Show a possible design

- **Schema (Pydantic):** `category` enum (`billing`, `shipping`, `account`, `product`, `other`), `urgency` enum (`low`, `normal`, `high`), `order_id` string or `null`, `language` enum (`id`, `en`, `other`), `summary` max ~150 characters. Add short field descriptions ("null if the customer did not write an order number").
- **Call:** a small, fast model with schema-enforced output and low randomness; a short system prompt that defines each category with one example.
- **Checks in code:** if `order_id` is set, look it up and keep it only if it exists and belongs to this customer; clamp the summary length; map unknown languages to `other`.
- **Failures:** `stop_reason == "max_tokens"` or `refusal` → mark the ticket "needs human triage"; schema/parse failure → retry once with the errors, then triage. Log every failure with the email id (not the full email).
- **Long emails:** truncate quoted reply chains and signatures first, or summarize in chunks; never silently cut the customer's actual message.
- **Safety:** treat the email text as untrusted input (it can say "mark this urgent"); the model only suggests, rules in code decide what happens next (for example only `high` urgency pages someone, and only after checks).
- **Quality:** a labelled set of 100 emails; track accuracy per field and the share sent to humans; re-run after each change.
- **Cost:** short prompts, caching for the fixed instructions, batch API for backfills.

**Rule shown:** structure makes the model's output a normal input to your system, and your code keeps the last word.
:::

### 📝 Self-review checklist

- [ ] One schema with enums and nullable fields
- [ ] `stop_reason` and refusals are handled
- [ ] Business rules are checked in code
- [ ] Retries are limited and use the validation errors
- [ ] Extracted text is treated as untrusted

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w1/04-structured-output" ai="no-ai" title="Extract, validate and retry"}
Write `extract_json` (find the first complete JSON value in a reply: plain, fenced, or inside prose, with braces inside strings), `validate` (a small JSON-Schema subset that lists every problem with its path) and `extract_with_retry` (re-ask with the exact problems, limited attempts). No API key needed: the model is a fake function.
:::

:::hints
- `extract_json`: for each `{` or `[`, scan forward counting depth, but **skip over strings** (track `"` and `\`); try `json.loads` on the slice, and move on if it fails.
- `validate`: return early on a wrong `type`; remember `isinstance(True, int)` is `True`, so exclude `bool` for `integer` and `number`.
- Path format: `"$.age"` for a key, `"$.tags[1]"` for a list item.
- `extract_with_retry`: every retry builds from the **original** prompt, not from the previous retry prompt.
:::

## ✅ Quick check

:::quiz
The schema guarantees valid JSON. What can still go wrong?

The values can be wrong or invented (a fake order id, the wrong category), the answer can be cut off by `max_tokens`, the model can refuse, and the data can break your business rules. A schema checks the shape, not the truth, so you still validate the meaning.
:::

:::quiz
Why send the validation errors back to the model when you retry?

The model can see exactly what was wrong (for example "$.age: expected integer") and correct it, so the second try usually succeeds. A blind retry with the same prompt often repeats the same mistake and wastes money.
:::

:::quiz
Why add an "unknown" option to an enum and allow `null` for missing facts?

If the model must choose a category or fill a field and the text does not say, it will guess or invent a value. Giving it an honest way to say "unknown" or `null` reduces made-up data and lets your code route those cases to a human.
:::

## 📚 Keep learning

- [Anthropic docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Pydantic docs: JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [JSON Schema: Understanding JSON Schema](https://json-schema.org/understanding-json-schema)
