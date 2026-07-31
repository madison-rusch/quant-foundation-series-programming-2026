# Common Algorithms — Overview

The runnable companion is [algorithms.py](algorithms.py) — every function has a self-check
in `main()`, so you can run it, trust it, and step through it in the debugger:

```bash
python lessons/lesson-05-equity-analysis-capstone/demos/02-algorithms/algorithms.py
```

You will almost never hand-write these in a real quant job — pandas, NumPy, and Python's
built-ins do it faster and more safely than you can. So why learn them? Because interviewers
ask, and because understanding *how* they work is how you understand *why* one operation is
`O(log n)` and another `O(n²)`. See [big-o-notation.md](../01-big-o-notation/big-o-notation.md) for the complexity
language used throughout.

## Searching

### Linear search — O(n)
Walk the list until you find the target. Works on any list, sorted or not. It's what
`x in my_list` does under the hood.

### Binary search — O(log n)
Repeatedly halve a **sorted** range: check the middle, then discard the half that can't
contain the target.

```python
lo, hi = 0, len(values) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if values[mid] == target:  return mid
    if values[mid] < target:   lo = mid + 1   # go right
    else:                      hi = mid - 1   # go left
return -1
```

**When it matters:** searching the same dataset many times. Sorting once (`O(n log n)`)
so that each of thousands of lookups is `O(log n)` beats scanning (`O(n)`) every time. The
precondition — *the data must be sorted* — is the classic thing interviewers check you remember.

## Sorting

You'll call `sorted()` or `df.sort_values()` in practice. These are here to build intuition.

| Algorithm | Complexity | Idea | Use in practice? |
|---|---|---|---|
| Bubble sort | O(n²) | Swap adjacent out-of-order pairs, repeat | No — teaching only |
| Insertion sort | O(n²), O(n) if nearly sorted | Insert each item into its place in a growing sorted prefix | Only for tiny/nearly-sorted inputs |
| Merge sort | O(n log n) | Split in half, sort each, merge | The classic stable O(n log n) |
| Timsort (Python built-in) | O(n log n) | Hybrid of merge + insertion, tuned for real data | **Yes — this is what you actually use** |

**Why merge sort is O(n log n):** halving the list gives `log n` levels; merging touches all
`n` items at each level. `n` work × `log n` levels = `O(n log n)`. That product is the floor
for any comparison-based sort — you can't beat it in general.

**Stability** (a detail interviewers like): a *stable* sort keeps equal elements in their
original order. It matters when you sort by one key after another — e.g. sort trades by time,
then by symbol, and you want same-symbol trades to stay time-ordered. Python's sort is stable.

## Recursion

A function that calls itself on a smaller version of the problem. Every recursion needs:

1. a **base case** that stops (no base case → infinite recursion → `RecursionError`), and
2. a **recursive case** that moves *toward* the base case.

```python
def factorial(n):
    if n <= 1:            # base case
        return 1
    return n * factorial(n - 1)   # recursive case, n gets smaller
```

**Recursion vs iteration:** anything recursive can be written as a loop and vice versa. Recursion
reads beautifully for naturally-nested problems (trees, divide-and-conquer like merge sort). The
cost is a function call per level — Python caps recursion depth (~1000) and has no
tail-call optimization, so very deep recursion should be a loop instead.

### The memoization trap (and fix)

Naive recursive Fibonacci recomputes the same subproblems exponentially often — `O(2ⁿ)`, which
crawls by `n=40`:

```python
def fib_slow(n):
    if n <= 1: return n
    return fib_slow(n - 1) + fib_slow(n - 2)     # recomputes the same values over and over
```

Cache each solved subproblem and it collapses to `O(n)`:

```python
def fib(n, cache=None):
    if cache is None: cache = {}
    if n <= 1: return n
    if n in cache: return cache[n]               # reuse instead of recompute
    cache[n] = fib(n - 1, cache) + fib(n - 2, cache)
    return cache[n]
```

This "store answers to subproblems" idea is the seed of **dynamic programming**. In finance it
shows up in binomial option-pricing trees, optimal-execution schedules, and path-dependent
Monte Carlo — anywhere the same intermediate state recurs.

## Where this shows up in quant work

- **Binary search** → looking up a date/level in a sorted time series; `numpy.searchsorted`,
  `bisect`, `pandas.merge_asof` are all binary-search-powered.
- **Sorting** → ranking assets by return, ordering a book by price, building league tables.
- **Recursion / dynamic programming** → binomial and trinomial trees, yield-curve bootstrapping,
  dynamic hedging and optimal-execution problems.
- **Hashing (O(1) lookup)** → dict/set as the fix for an accidental `O(n²)` — the single most
  common "make it faster" move in an interview.

## Further reading

- *Grokking Algorithms* by Aditya Bhargava — illustrated, beginner-friendly, covers all of the above.
- VisuAlgo: <https://visualgo.net/en/sorting> — watch the sorts run step by step.
- *Introduction to Algorithms* (CLRS) — the rigorous reference, for when you want the proofs.
- **Practice with Claude:** *"Give me a binary search problem, let me attempt it, then critique my
  solution and its complexity."*
