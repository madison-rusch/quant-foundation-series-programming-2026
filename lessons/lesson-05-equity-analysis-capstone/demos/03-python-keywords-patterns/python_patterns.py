"""
Self-review: Python keywords & patterns interviewers ask about.

lambda, comprehensions, generators, decorators — plus a few keywords that trip
people up (yield, with, *args/**kwargs). Each block is short, annotated, and
finance-flavoured. Read it top to bottom; run it to see the output.

Run from the repo root:
    python lessons/lesson-05-equity-analysis-capstone/demos/03-python-keywords-patterns/python_patterns.py
"""

import functools
import time
from collections.abc import Iterator


# ==========================================================================
# 1. lambda — a small anonymous function, defined inline.
# ==========================================================================
def lambda_examples() -> None:
    """Use a lambda for a throwaway function you pass as an argument."""
    tickers = [
        {"symbol": "AAPL", "weight": 0.07},
        {"symbol": "MSFT", "weight": 0.06},
        {"symbol": "NVDA", "weight": 0.09},
    ]
    # Sort by a computed key — the classic, idiomatic use of lambda.
    heaviest_first = sorted(tickers, key=lambda t: t["weight"], reverse=True)
    print("  heaviest holding:", heaviest_first[0]["symbol"])

    # map/filter take a function; a lambda saves naming a one-liner.
    weights = [t["weight"] for t in tickers]
    as_bps = list(map(lambda w: w * 10_000, weights))  # weights in basis points
    print("  weights in bps:  ", as_bps)

    # Rule of thumb: if the lambda needs a comment or a name, write a `def`.

# ==========================================================================
# 2. Comprehensions — build a list/dict/set in one readable expression.
# ==========================================================================
def comprehension_examples() -> None:
    """List, dict, and set comprehensions — Pythonic replacements for build-up loops."""
    prices = [100.0, 101.5, 99.2, 103.1, 98.7]

    # List comprehension with a condition (a filter): up-days only.
    daily_returns = [
        prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))
    ]
    up_days = [r for r in daily_returns if r > 0]
    print(f"  {len(up_days)} up-days out of {len(daily_returns)}")

    # Dict comprehension: symbol -> price.
    symbols = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOG"]
    book = {sym: price for sym, price in zip(symbols, prices)}
    print("  price book:", book)

    # Set comprehension: unique sectors, deduped automatically.
    sectors = ["Tech", "Tech", "Energy", "Tech", "Energy"]
    unique = {s for s in sectors}
    print("  unique sectors:", unique)

    # Nested comprehension: flatten a grid of scenario P&Ls.
    grid = [[1, -2], [3, -4], [5, -6]]
    flat = [pnl for row in grid for pnl in row]
    print("  flattened P&L:", flat)


# ==========================================================================
# 3. Generators & `yield` — produce values lazily, one at a time.
# ==========================================================================
def rolling_windows(values: list[float], size: int) -> Iterator[list[float]]:
    """
    Yield successive windows of `size` items without building them all at once.

    A generator holds one window in memory, not the whole list of windows — the
    reason they matter for large market-data streams you can't fit in RAM.
    """
    for i in range(len(values) - size + 1):
        yield values[i : i + size]  # `yield` hands back one value, then pauses here


def generator_examples() -> None:
    """Show lazy evaluation and a generator expression."""
    prices = [100.0, 102.0, 101.0, 105.0, 104.0]

    # Each window is computed only when the loop asks for it.
    for window in rolling_windows(prices, size=3):
        avg = sum(window) / len(window)
        print(f"  window {window} -> 3-day avg {avg:.2f}")

    # Generator expression: like a list comprehension but lazy (parentheses, not
    # brackets). sum() consumes it without ever materializing the full list.
    total_abs_move = sum(abs(prices[i] - prices[i - 1]) for i in range(1, len(prices)))
    print(f"  total absolute move: {total_abs_move:.2f}")


# ==========================================================================
# 4. Decorators — wrap a function to add behaviour without editing its body.
# ==========================================================================
def timed(func):
    """A decorator that prints how long the wrapped function took."""

    @functools.wraps(func)  # preserve the wrapped function's name/docstring
    def wrapper(*args, **kwargs):  # *args/**kwargs forward any arguments through
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"  [{func.__name__}] took {elapsed_ms:.2f} ms")
        return result

    return wrapper


@timed  # sugar for: slow_sum = timed(slow_sum)
def slow_sum(n: int) -> int:
    """Sum 0..n-1 the slow, explicit way — just to have something to time."""
    return sum(range(n))


def decorator_examples() -> None:
    """Call the decorated function; the timing print comes from the decorator."""
    result = slow_sum(1_000_000)
    print(f"  result: {result}")
    # functools.wraps kept the identity intact:
    print(f"  slow_sum.__name__ is still '{slow_sum.__name__}'")


# ==========================================================================
# 5. `with` — context managers that clean up after themselves.
# ==========================================================================
def with_statement_example() -> None:
    """`with` guarantees teardown (closing a file) even if the body raises."""
    from io import StringIO

    # StringIO is an in-memory file — same interface, no disk needed for the demo.
    with StringIO("AAPL,100\nMSFT,101\n") as handle:
        rows = [line.strip().split(",") for line in handle]
    # Outside the block the handle is closed automatically — no manual .close().
    print("  parsed rows:", rows)


def main() -> None:
    print("1. lambda:")
    lambda_examples()
    print("\n2. comprehensions:")
    comprehension_examples()
    print("\n3. generators & yield:")
    generator_examples()
    print("\n4. decorators:")
    decorator_examples()
    print("\n5. with / context managers:")
    with_statement_example()


if __name__ == "__main__":
    main()
