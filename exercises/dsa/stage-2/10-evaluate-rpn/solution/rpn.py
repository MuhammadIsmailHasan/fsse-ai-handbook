OPERATORS = {"+", "-", "*", "/"}


# Time O(n), space O(n).
def evaluate_rpn(tokens: list[str]) -> int:
    stack: list[int] = []
    for token in tokens:
        if token in OPERATORS:
            if len(stack) < 2:
                raise ValueError(f"not enough operands for {token!r}")
            right = stack.pop()
            left = stack.pop()
            if token == "+":
                stack.append(left + right)
            elif token == "-":
                stack.append(left - right)
            elif token == "*":
                stack.append(left * right)
            else:
                if right == 0:
                    raise ZeroDivisionError("division by zero")
                quotient = abs(left) // abs(right)
                stack.append(quotient if (left >= 0) == (right > 0) else -quotient)
        else:
            try:
                stack.append(int(token))
            except ValueError:
                raise ValueError(f"unknown token {token!r}") from None
    if len(stack) != 1:
        raise ValueError("invalid expression")
    return stack[0]
