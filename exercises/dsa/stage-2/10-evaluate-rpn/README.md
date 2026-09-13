# DSA · Stage 2 · Calculator in Reverse Polish Notation

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

In Reverse Polish Notation (RPN), operators come **after** their operands: `3 4 +` means `3 + 4`. No parentheses needed — a stack does all the work.

`evaluate_rpn(tokens)`:

```python
evaluate_rpn(["2", "1", "+", "3", "*"])          # 9   ((2 + 1) * 3)
evaluate_rpn(["4", "13", "5", "/", "+"])         # 6   (4 + 13 / 5)
evaluate_rpn(["-7", "2", "/"])                   # -3  (division truncates toward zero)
```

- Tokens are integers (may be negative, like `"-7"`) or one of `+ - * /`
- `/` truncates **toward zero** (`-7 / 2 → -3`, not `-4`)
- Raise `ValueError` for invalid expressions: not enough operands, leftover operands, unknown tokens, empty input
- Raise `ZeroDivisionError` for division by zero

```bash
cd exercises
uv run pytest dsa/stage-2/10-evaluate-rpn
```
