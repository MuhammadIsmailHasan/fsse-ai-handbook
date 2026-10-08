class MinHeap:
    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)

    def peek(self):
        if not self.items:
            raise IndexError("peek from empty heap")
        return self.items[0]

    def push(self, value):
        items = self.items
        items.append(value)
        i = len(items) - 1
        while i > 0:
            parent = (i - 1) // 2
            if items[parent] <= items[i]:
                break
            items[parent], items[i] = items[i], items[parent]
            i = parent

    def pop(self):
        items = self.items
        if not items:
            raise IndexError("pop from empty heap")
        smallest = items[0]
        last = items.pop()
        if items:
            items[0] = last
            i, n = 0, len(items)
            while True:
                left, right, small = 2 * i + 1, 2 * i + 2, i
                if left < n and items[left] < items[small]:
                    small = left
                if right < n and items[right] < items[small]:
                    small = right
                if small == i:
                    break
                items[i], items[small] = items[small], items[i]
                i = small
        return smallest


def heap_sort(values):
    heap = MinHeap()
    for v in values:
        heap.push(v)
    return [heap.pop() for _ in range(len(heap))]
