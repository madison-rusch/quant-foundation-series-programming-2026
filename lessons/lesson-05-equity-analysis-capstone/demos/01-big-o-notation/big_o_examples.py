"""
Self-review: Big O notation, by example.

Big O describes how an algorithm's work grows as its input grows — not how many
seconds it takes on your laptop. We care because a choice that's fine on 100 rows
can freeze on 10 million: exactly the jump you make going from a classroom CSV to
a real market-data set.

Each function below is one complexity class, with a finance-flavoured example.
main() times them at growing input sizes so you can *see* the growth curve.

Run from the repo root:
    python lessons/lesson-05-equity-analysis-capstone/demos/01-big-o-notation/big_o_examples.py
"""

import time


# --------------------------------------------------------------------------
# O(1) — constant. Work doesn't grow with input size.
# --------------------------------------------------------------------------
def latest_price(prices: list[float]) -> float:
    """Return the most recent price. One indexing op, no matter how long the list."""
    return prices[-1]


# --------------------------------------------------------------------------
# O(log n) — logarithmic. Each step halves the remaining work.
# --------------------------------------------------------------------------
def binary_search(sorted_prices: list[float], target: float) -> int:
    """Find target's index in a SORTED list, halving the search range each step."""
    lo, hi = 0, len(sorted_prices) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_prices[mid] == target:
            return mid
        if sorted_prices[mid] < target:
            lo = mid + 1  # discard the lower half
        else:
            hi = mid - 1  # discard the upper half
    return -1


# --------------------------------------------------------------------------
# O(n) — linear. Touch each element once.
# --------------------------------------------------------------------------
def total_volume(volumes: list[int]) -> int:
    """Sum every element — work grows in direct proportion to the input size."""
    running = 0
    for v in volumes:  # one pass over n elements
        running += v
    return running


# --------------------------------------------------------------------------
# O(n log n) — the cost of a good general-purpose sort.
# --------------------------------------------------------------------------
def sorted_returns(returns: list[float]) -> list[float]:
    """Sort returns ascending. Python's built-in sort (Timsort) is O(n log n)."""
    return sorted(returns)  # n elements, each participating in log n merge levels


# --------------------------------------------------------------------------
# O(n^2) — quadratic. A nested loop over the same input. Watch this one blow up.
# --------------------------------------------------------------------------
def any_duplicate_price_slow(prices: list[float]) -> bool:
    """Compare every pair of prices — n * n work. The naive, quadratic way."""
    n = len(prices)
    for i in range(n):
        for j in range(i + 1, n):  # for each element, scan the rest
            if prices[i] == prices[j]:
                return True
    return False


def any_duplicate_price_fast(prices: list[float]) -> bool:
    """Same question, O(n): a set membership test is ~O(1), done once per element."""
    seen: set[float] = set()
    for p in prices:
        if p in seen:  # set lookup is roughly constant time
            return True
        seen.add(p)
    return False


def _time_call(fn, *args) -> float:
    """Return wall-clock milliseconds for one call to fn."""
    start = time.perf_counter()
    fn(*args)
    return (time.perf_counter() - start) * 1000


def main() -> None:
    print("How runtime grows with input size n (milliseconds):\n")
    header = f"{'n':>8} | {'O(n) sum':>10} | {'O(n log n) sort':>16} | {'O(n^2) dupes':>13}"
    print(header)
    print("-" * len(header))

    for n in (10_000, 20_000, 40_000, 80_000):
        data = list(range(n))  # already-unique data forces the full n^2 scan
        t_linear = _time_call(total_volume, data)
        t_sort = _time_call(sorted_returns, [float(x) for x in data])
        t_quad = _time_call(any_duplicate_price_slow, [float(x) for x in data])
        print(f"{n:>8} | {t_linear:>10.3f} | {t_sort:>16.3f} | {t_quad:>13.3f}")

    print(
        "\nNote how doubling n roughly doubles the O(n) column, but roughly "
        "QUADRUPLES the O(n^2) column — that's the trap quadratic code sets."
    )

    # Same problem, two complexities — the point of the fast/slow pair above.
    # All-unique data is the worst case: both must inspect everything, so the
    # only difference you see is the complexity class, not lucky early exits.
    big = [float(x) for x in range(10_000)]  # no duplicates anywhere
    print(f"\nDuplicate check on {len(big):,} unique items (worst case):")
    print(f"  O(n^2) version: {_time_call(any_duplicate_price_slow, big):.1f} ms")
    print(f"  O(n)   version: {_time_call(any_duplicate_price_fast, big):.3f} ms")


if __name__ == "__main__":
    main()
