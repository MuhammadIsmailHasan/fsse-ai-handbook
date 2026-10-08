# Module 7 · W2 · Guardrails

> 🚫🤖 **No-AI** · ⏱️ ~50 min · no API key needed

A model is polite, but it is not a security guard. Safety comes from checks that **your code** runs at three moments:

```text
user text ──► [INPUT checks] ──► model ──► [OUTPUT checks] ──► user
                                   │
                                   └─ tool call ──► [TOOL policy] ──► run / ask a human / refuse
```

| Function | Moment | Does |
|---|---|---|
| `redact_pii(text)` | input and output | hide emails, card numbers (Luhn-checked, so order numbers survive) and Indonesian phone numbers |
| `injection_signals(text)` | input | name the prompt-injection patterns found ("ignore previous instructions", "reveal your prompt", ...) |
| `check_output(text, secrets)` | output | your secrets leaked? too long? personal data in the answer? |
| `authorize(tool, args, policy)` | tool call | `allow`, `needs_approval` (a refund over the limit) or `deny` (unknown tool, or an amount that is not a number) |

Be honest about their limits: pattern lists miss clever attacks, and they flag some innocent text. Use them for **logging, extra care and cheap blocks**, never as the only defence. The strongest guardrail is the last one: a tool policy that makes a harmful action impossible even if the model is fooled.

```bash
cd exercises
uv run pytest m7/w2/03-guardrails
```
