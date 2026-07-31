"""
Self-review: common algorithms every quant should recognize.

You will rarely hand-write a sort in a real job — pandas and NumPy do it for you.
But interviewers ask, and understanding *how* they work tells you *why* one is
O(n log n) and another O(n^2). Each function below has a one-line complexity note
and a tiny finance-flavoured example. main() runs self-checks so you can trust
the code and step through it in the debugger.

Run from the repo root:
    python lessons/lesson-05-equity-analysis-capstone/demos/02-algorithms/algorithms.py
"""


# ==========================================================================
# SEARCHING
# ==========================================================================
def binary_search(sorted_values: list[float], target: float) -> int:
    """
    Find target in a SORTED list; return its index or -1.  Complexity: O(log n).

    Each comparison throws away half the remaining range. The precondition is the
    whole trick: it only works because the input is sorted. On unsorted data you'd
    do a linear scan (O(n)) — or sort first (O(n log n)) if you'll search often.
    """
    lo, hi = 0, len(sorted_values) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_values[mid] == target:
            return mid
        if sorted_values[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ==========================================================================
# SORTING
# ==========================================================================
def bubble_sort(values: list[float]) -> list[float]:
    """
    Teaching sort: repeatedly swap adjacent out-of-order pairs.  O(n^2).

    Never use this in production — it's here so you can *see* why nested passes
    make it quadratic. Returns a new list; leaves the input untouched.
    """
    items = list(values)  # copy — don't mutate the caller's list
    n = len(items)
    for i in range(n):
        swapped = False
        # After pass i, the last i items are already in place, so stop early.
        for j in range(0, n - i - 1):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
                swapped = True
        if not swapped:  # a clean pass means we're already sorted
            break
    return items


def insertion_sort(values: list[float]) -> list[float]:
    """
    Build the sorted list one item at a time.  O(n^2) worst case, O(n) if nearly
    sorted — which is why it's the building block inside real hybrid sorts.
    """
    items = list(values)
    for i in range(1, len(items)):
        key = items[i]
        j = i - 1
        # Shift larger items right until key lands in its sorted position.
        while j >= 0 and items[j] > key:
            items[j + 1] = items[j]
            j -= 1
        items[j + 1] = key
    return items


def merge_sort(values: list[float]) -> list[float]:
    """
    Divide and conquer: split in half, sort each half, merge.  O(n log n).

    The log n comes from halving the list; the n from merging at each level. This
    is the complexity class of every good general-purpose sort (including the
    Timsort behind Python's built-in `sorted`).
    """
    if len(values) <= 1:  # base case: a 0- or 1-element list is already sorted
        return list(values)
    mid = len(values) // 2
    left = merge_sort(values[:mid])
    right = merge_sort(values[mid:])
    return _merge(left, right)


def _merge(left: list[float], right: list[float]) -> list[float]:
    """Merge two already-sorted lists into one sorted list. O(n)."""
    merged: list[float] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])  # whichever side has leftovers is already sorted
    merged.extend(right[j:])
    return merged


# ==========================================================================
# RECURSION
# ==========================================================================
def factorial(n: int) -> int:
    """
    n! via recursion — the textbook example.  O(n) calls deep.

    Every recursion needs a BASE CASE (here n <= 1) or it never stops. Used in
    finance for combinatorics: e.g. counting the ways to order settlement legs.
    """
    if n < 0:
        raise ValueError("factorial is undefined for negative n")
    if n <= 1:  # base case
        return 1
    return n * factorial(n - 1)  # recursive case, moving toward the base case


def compound_recursive(principal: float, rate: float, periods: int) -> float:
    """
    Future value by compounding one period at a time, recursively.  O(periods).

    rate: per-period, as a decimal (0.05 == 5%). A clearer-than-usual recursion:
    each call peels off one period. The closed form principal*(1+rate)**periods is
    what you'd actually ship — this just makes the recursive structure visible.
    """
    if periods == 0:  # base case: no more periods to compound
        return principal
    return compound_recursive(principal * (1 + rate), rate, periods - 1)


def fibonacci_memo(n: int, cache: dict[int, int] | None = None) -> int:
    """
    n-th Fibonacci number with MEMOIZATION.  O(n) with the cache; O(2^n) without.

    The naive version recomputes the same subproblems exponentially often — a
    classic "why is this so slow?" bug. Caching solved subproblems is the fix, and
    the core idea behind dynamic programming.
    """
    if cache is None:
        cache = {}
    if n <= 1:
        return n
    if n in cache:  # already solved this subproblem — reuse it
        return cache[n]
    cache[n] = fibonacci_memo(n - 1, cache) + fibonacci_memo(n - 2, cache)
    return cache[n]


def main() -> None:
    prices = [98.5, 101.2, 99.9, 103.4, 100.0, 97.3, 105.1]
    expected = sorted(prices)

    print("Sorting (each must match Python's sorted):")
    for name, fn in (
        ("bubble_sort", bubble_sort),
        ("insertion_sort", insertion_sort),
        ("merge_sort", merge_sort),
    ):
        result = fn(prices)
        status = "OK" if result == expected else "FAIL"
        print(f"  {name:<16} {status}")

    print("\nBinary search (on the sorted prices):")
    target = 103.4
    idx = binary_search(expected, target)
    print(f"  found {target} at index {idx} -> {expected[idx]}")
    print(f"  missing value 42.0 -> index {binary_search(expected, 42.0)} (expected -1)")

    print("\nRecursion:")
    print(f"  factorial(6)                = {factorial(6)}  (expected 720)")
    fv = compound_recursive(1000.0, 0.05, 3)
    print(f"  compound(1000, 5%, 3yrs)    = {fv:.2f}  (expected 1157.62)")
    print(f"  fibonacci_memo(30)          = {fibonacci_memo(30)}  (expected 832040)")


if __name__ == "__main__":
    main()
