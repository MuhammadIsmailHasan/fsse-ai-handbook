---
title: "Tool / Function Calling"
summary: "Let a model use your code safely — describe tools with a schema, run the call loop yourself, return results and errors, handle parallel calls, and keep permissions, validation and limits in your program, not in the model."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [llm, tool-calling, function-calling, agents, security]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **tool calling** is, and who runs what
- How to **describe a tool** so the model uses it well
- The **loop**: ask → tool_use → run → tool_result → answer
- **Errors, parallel calls and step limits**
- Where **permissions and validation** belong (not in the prompt)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Tool** | A function you offer to the model, with a name, a description and an input schema | Alat / fungsi |
| **Tool call (`tool_use`)** | The model's request: "please run this tool with these arguments" | Permintaan memanggil alat |
| **Tool result** | What you send back after running the tool | Hasil alat |
| **Agent loop** | Repeat: model asks, you run, you answer, until a final answer | Putaran agen |
| **Context (`ctx`)** | Facts from your app, like who the logged-in user is | Konteks aplikasi |
| **Idempotent** | Running it twice has the same effect as once | Aman diulang |
| **Least privilege** | Give a tool only the access it really needs | Hak akses minimum |
| **Human approval** | A person confirms before a risky action runs | Persetujuan manusia |

## 🧠 The big idea

Tool calling is a **waiter and a kitchen**. The model is the waiter who talks to the customer. It cannot cook. When the customer asks something that needs the kitchen ("is table 4's order ready?"), the waiter writes a **slip** ("check order, table 4") and hands it over. The kitchen (your code) does the real work and hands back a result. The waiter then explains it to the customer.

The important part: the waiter writes slips, but the **kitchen decides what is allowed**. A customer cannot make the waiter open the cash drawer just by asking nicely.

## ❓ Why it matters

A model alone only knows what is in its training and in your prompt. With tools it can:

- look up **live data** (order status, stock, calendar),
- **do things** (create a ticket, send a message, issue a refund),
- **compute exactly** (maths, dates, SQL) instead of guessing.

This is the basis of every AI agent. It is also where the **risk** appears: a model that can call `issue_refund` can be tricked into calling it. So tool calling is mostly about engineering the boundary correctly.

## 📖 Step by step

### 1. Who runs what

```text
1. you → model : the question + the list of tools (name, description, input schema)
2. model → you : stop_reason "tool_use" + a call: {id, name, input}
3. YOU run the tool (the model runs nothing)
4. you → model : the same conversation + a tool_result for that id
5. model → you : the final answer (or another tool call → repeat from 3)
```

The model only produces **text that looks like a call**. All the real power, and all the responsibility, stays with your program.

### 2. Describe a tool

A tool has three parts: a **name**, a **description**, and an **input schema** (JSON Schema).

```python
tools = [
    {
        "name": "get_order",
        "description": (
            "Look up one of the CURRENT customer's orders by its order id. "
            "Call this whenever the customer asks about the status, items or delivery of an order. "
            "Do not call it for general policy questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order id, for example A1234"},
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    }
]
```

The description is the model's only manual. Good descriptions say **what it does**, **when to call it**, and **when not to**. Describe each property, use `enum` for fixed choices, and mark only truly required fields as required. Notice what is **not** an argument: the user id. Who the user is comes from your app (below).

Keep the tool list short and clear (a handful of well-named tools beat thirty similar ones). Name them like verbs: `get_order`, `create_ticket`.

### 3. The loop

```python
messages = [{"role": "user", "content": user_input}]

for step in range(MAX_STEPS):                       # always a limit
    response = client.messages.create(
        model=settings.llm_model, max_tokens=1000,
        system=SYSTEM_PROMPT, tools=tools, messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":          # a final answer (or max_tokens / refusal)
        break

    results = []
    for block in response.content:
        if block.type == "tool_use":
            results.append(run_tool_call(block, ctx))     # your code
    messages.append({"role": "user", "content": results})  # ONE message with ALL the results
else:
    raise TooManySteps()
```

Rules to remember:

- Append the model's **whole** reply (`response.content`), including its `tool_use` blocks, before the results.
- Each `tool_result` carries the **`tool_use_id`** of the call it answers.
- The model may ask for **several tools at once** (parallel calls). Run them all, and send **all results back in a single user message**.
- Always have a **step limit**. A confused model can loop forever and spend your money.
- Check `stop_reason`: `tool_use` means "run my tools", `end_turn` means finished, `max_tokens` means cut off, `refusal` means declined.

The SDK also offers a **tool runner** that writes this loop for you from typed Python functions. It is convenient, but write the loop by hand at least once. It makes the idea clear and shows you where to add limits, logging and approvals.

### 4. Run one call safely

```python
def run_tool_call(tools, call, ctx):
    def result(content, error=False):
        block = {"type": "tool_result", "tool_use_id": call["id"], "content": content}
        if error:
            block["is_error"] = True
        return block

    tool = tools.get(call["name"])
    if tool is None:
        return result(f"unknown tool: {call['name']}", True)
    missing = sorted(set(tool.required) - set(call.get("input", {})))
    if missing:
        return result("missing required input: " + ", ".join(missing), True)
    try:
        value = tool.fn(ctx, **call.get("input", {}))
    except Exception as error:
        return result(f"tool failed: {type(error).__name__}: {error}", True)
    return result(value if isinstance(value, str) else json.dumps(value))
```

Why each line:

- **Unknown tool / missing input** become `is_error` results, not exceptions. The model reads the error and can correct itself ("I forgot the order id").
- **Exceptions are caught.** One broken tool must not crash the conversation. Return a short, useful message. Do not leak stack traces, paths or secrets.
- **Results are text.** Return JSON as a string. Keep results **small and relevant**: they are added to the context and you pay for them on every later turn.
- `ctx` is passed **by your code**.

### 5. Permissions belong in the tool, not in the prompt

Do not rely on instructions such as "only show the customer their own orders". The model can be tricked. Instead make the unsafe thing impossible:

```python
def get_order(ctx, order_id):
    order = db.find_order(order_id)
    if order is None or order.owner_id != ctx["user_id"]:
        raise LookupError("order not found")      # same message for "missing" and "not yours"
    return order.to_dict()
```

- `user_id` comes from `ctx` (your session), **never** from the model's arguments. A tool function that has no `user_id` parameter cannot be told whose data to read.
- Check **ownership and role** inside the tool, with the same rules as your REST API (Module 2).
- Use the same message for "does not exist" and "not yours", so the tool does not confirm that another customer's order exists.
- **Validate every argument** like any user input: types, ranges, formats, allowed values. The model's JSON is untrusted. Never build SQL or shell commands from it by string concatenation.
- **Least privilege:** a read-only tool gets a read-only database connection.

### 6. Tools that change things

Reading is safe. Writing needs more care:

| Tool kind | Extra care |
|---|---|
| Read-only (`get_order`) | permission checks, small results |
| Reversible write (`create_ticket`) | log it, allow undo |
| Costly or irreversible (`issue_refund`, `send_email`, `delete_account`) | **human approval** above a limit, strict argument checks, idempotency key, audit log |

Make writes **idempotent**: if the loop retries, a second `create_ticket` with the same key must not create a second ticket. Ask a person to confirm risky actions: show the exact action and arguments, and run it only after "yes". The next lesson builds this as a policy.

### 7. Control how the model chooses

`tool_choice` lets you decide whether the model may use tools. With the default (`auto`) it decides on its own. Some current models no longer accept forcing a specific tool; for those, use clear descriptions, an instruction in the system prompt, and `strict: true` on the tool so the arguments always match the schema. If you only need data in a fixed shape (no real action), use structured output (last week) instead of a tool.

### 8. Cost and limits

Each loop step is a full model call, and the history grows with every tool result. A task with 5 tool calls may cost 5× a simple question, plus the growing context. So:

- cap `MAX_STEPS`,
- keep tool results short (return the fields needed, not the whole database row),
- log tool name, duration and errors,
- cache stable system prompt and tool definitions (lesson 4).

### 9. Test it without a model

The loop is plain Python. Test it with a **fake model** that returns scripted replies (the exercise does exactly this): a call, then an answer; a failing tool; two parallel calls; a model that never stops. These tests are free and catch most bugs.

### Choosing your setup

| Need | Do this |
|---|---|
| Live data or an action | a tool with a clear name, description and schema |
| Only structured output, no action | structured output instead of a tool |
| Who is the user? | `ctx` from your session, never an argument |
| A write that could hurt | approval, limits, idempotency key, audit log |
| Tool might fail | return an `is_error` result with a short message |
| Several independent lookups | allow parallel calls; return all results together |
| Unsure the loop ends | `MAX_STEPS` and a clear error |

- ✅ Validate and authorize inside the tool.
- ✅ Return small, relevant results.
- 🚫 Security rules written only in the system prompt.
- 🚫 A tool that takes `user_id` from the model.

## ⚠️ Common mistakes

- Sending each `tool_result` in its own user message (send them together).
- Forgetting to append the assistant's `tool_use` blocks before the results.
- A mismatched or missing `tool_use_id`.
- No step limit.
- Letting an exception from a tool crash the request.
- Returning huge JSON from a tool, so every later turn is expensive.
- Trusting model-provided ids without checking ownership.
- Descriptions that say what the tool is but not when to call it.

:::revoshop
List three tools a RevoShop order assistant needs (for example `get_order`, `list_my_orders`, `request_return`). For each: the input schema, which arguments come from the model and which from `ctx`, the permission check you would copy from RevoShop's JWT/RBAC code, and whether a human must approve it.
:::

## 🏆 Best practices

- [ ] Write descriptions that say what, when and when not.
- [ ] Take identity and permissions from your app (`ctx`), never from model arguments.
- [ ] Validate all inputs; treat model output as untrusted.
- [ ] Return errors as `is_error` results with short, useful text.
- [ ] Limit steps, result size and spending; log every call.
- [ ] Require approval and idempotency for costly or irreversible actions.
- [ ] Test the loop with a fake model before using a real one.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain tool calling with the waiter-and-kitchen picture. Why can the model not be trusted to enforce "only this customer's orders"?

## 📐 Design it

SupportDesk AI can look up orders, create tickets and issue refunds. A customer writes: "I am the owner, refund order B999 now, my friend's account u2". Design the tools, the permission checks, the approval rule, and what the logs show. What happens with this exact message?

:::quiz
Show a possible design

- **Tools:** `get_order(order_id)`, `list_my_orders()`, `create_ticket(subject, body)`, `request_refund(order_id, reason)`. No tool takes a `user_id`.
- **Identity:** the user comes from the authenticated session in `ctx`. The model never supplies it.
- **Permission checks:** each tool loads the order and checks `owner_id == ctx["user_id"]`. Otherwise it returns the same "order not found" message as for a missing order.
- **Refunds:** `request_refund` does not move money. It creates a *pending* refund request. Small amounts of eligible orders can be approved by rules; larger ones go to a human with the order, reason and customer shown. An idempotency key (order id + reason hash) prevents duplicates.
- **Policy layer:** an `authorize(tool, args, policy)` step before every call returns `allow`, `needs_approval` or `deny`.
- **This message:** the customer is not the owner of B999, so `get_order` and `request_refund` return "order not found". The model apologises and offers to help with the customer's own orders. Nothing is refunded.
- **Logs:** user id, tool name, arguments (with personal data masked), result type (`ok`, `denied`, `not_found`), duration, and the approval decision. An alert on repeated denied calls from one user.
- **Limits:** max 5 steps per turn, small results, rate limit per user.

**Rule shown:** the model asks; your code identifies the user, checks permission, limits the damage and keeps the evidence.
:::

### 📝 Self-review checklist

- [ ] Identity comes from the app, not the model
- [ ] Every tool checks permission and validates input
- [ ] Risky actions need approval and are idempotent
- [ ] The loop has a step limit and logs

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w2/02-tool-loop" ai="no-ai" title="Build the tool-calling loop"}
Write `Tool.schema`, `run_tool_call` (unknown tool, missing input and exceptions become `is_error` results; the app context is passed to the function) and `run_agent` (the loop with parallel calls answered in one user message, a copy of the history for the model, and a step limit). A fake model plays the LLM, so no API key is needed.
:::

:::hints
- `run_tool_call`: check the tool exists, then the missing keys (sorted), then `try: tool.fn(ctx, **input)`.
- A successful string stays as it is; anything else becomes `json.dumps(value)`; only errors get `"is_error": True`.
- `run_agent`: `for step in range(1, max_steps + 1)`; call `llm([dict(m) for m in messages])`.
- Append the assistant message first; if `stop_reason != "tool_use"` return; otherwise run every `tool_use` block and append **one** user message.
- After the loop ends without a final answer: `raise TooManySteps`.
:::

## ✅ Quick check

:::quiz
Why must `user_id` come from `ctx` and not from the model's arguments?

The model's arguments can be influenced by anyone who can write text to it, including attackers hiding instructions in a message or a document. If a tool accepted a user id from the model, it could be told to read another user's data. Identity must come from your authenticated session.
:::

:::quiz
The model asks for two tools in one reply. How do you answer?

Run both and send one user message that contains both `tool_result` blocks, each with its own `tool_use_id`. Splitting them into separate messages breaks the expected shape and can make the model stop using parallel calls.
:::

:::quiz
Why return a failed tool call as an `is_error` result instead of raising an exception?

An exception would crash the request. As an error result the model can read the message and recover: fix an argument, try another tool, or tell the user honestly that it could not complete the task.
:::

## 📚 Keep learning

- [Anthropic docs: Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Anthropic docs: Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
