# Module 7 · W2 · The Tool-Calling Loop

> 🚫🤖 **No-AI** · ⏱️ ~50 min · no API key needed

A model cannot look up an order or send an email. With **tool calling** it can *ask* your program to do it:

```text
you  → model : question + the list of tools it may use
model → you  : stop_reason "tool_use" + {name: "get_order", input: {order_id: "A1"}}
you run get_order("A1")   ← YOUR code, YOUR permissions
you  → model : the tool_result
model → you  : the final answer
```

| Piece | Does |
|---|---|
| `Tool.schema()` | the definition you send to the API |
| `run_tool_call(tools, call, ctx)` | run one call and **always** return a `tool_result` — unknown tool, missing input and exceptions become `is_error` results, never crashes |
| `run_agent(llm, tools, message, ctx, max_steps)` | the loop; parallel calls go back in **one** user message, in order; a step limit stops runaway loops |

The most important line in the tests: `ctx` (who the logged-in user is) comes from **your app**, never from the model. The model only supplies the arguments, and anything it supplies is untrusted.

```bash
cd exercises
uv run pytest m7/w2/02-tool-loop
```
