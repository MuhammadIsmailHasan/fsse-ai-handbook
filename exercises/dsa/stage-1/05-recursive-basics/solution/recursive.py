"""Reference solution."""


def sum_digits(n: int) -> int:
    if n < 10:  # base case: a single digit
        return n
    return n % 10 + sum_digits(n // 10)


def power(base: int, exp: int) -> int:
    if exp == 0:  # base case: anything to the power 0 is 1
        return 1
    half = power(base, exp // 2)  # O(log exp): halve the exponent each call
    return half * half if exp % 2 == 0 else half * half * base


def is_palindrome(text: str) -> bool:
    if len(text) <= 1:  # base case: empty or one character
        return True
    return text[0] == text[-1] and is_palindrome(text[1:-1])


def count_down(n: int) -> list[int]:
    if n == 0:  # base case
        return [0]
    return [n] + count_down(n - 1)
