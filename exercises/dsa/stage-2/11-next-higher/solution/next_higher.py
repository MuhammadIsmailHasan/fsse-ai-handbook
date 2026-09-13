# Time O(n): every index is pushed and popped at most once. Space O(n).
def days_until_higher(prices: list[int]) -> list[int]:
    answer = [0] * len(prices)
    waiting: list[int] = []  # indices with decreasing (non-increasing) prices
    for day, price in enumerate(prices):
        while waiting and prices[waiting[-1]] < price:
            earlier = waiting.pop()
            answer[earlier] = day - earlier
        waiting.append(day)
    return answer
