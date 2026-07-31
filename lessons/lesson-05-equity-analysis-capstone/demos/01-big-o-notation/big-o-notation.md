# Big O Notation — Reference

Work through this at your own pace. The runnable companion is
[big_o_examples.py](big_o_examples.py) — run it and watch the growth curves appear:

```bash
python lessons/lesson-05-equity-analysis-capstone/demos/01-big-o-notation/big_o_examples.py
```

## What Big O actually is

Big O describes **how the amount of work grows as the input grows** — not seconds,
not megabytes, and not how fast your laptop is. We drop constants and lower-order
terms and keep only the dominant one, because that's what decides whether your code
survives when the data gets big.

> A quant analogy: Big O is *duration*, not *price*. It tells you how sensitive your
> runtime is to a change in input size, the same way duration tells you how sensitive
> a bond's price is to a change in rates.

Why you care: an approach that's instant on a 200-row classroom CSV can hang for
minutes on a few million ticks of market data. The complexity class tells you *before*
you run it whether it will scale.

## The five you must recognize

| Notation | Name | Plain English | Doubling `n` means… | Everyday example |
|---|---|---|---|---|
| `O(1)` | Constant | Same work regardless of size | No change | `prices[-1]`, dict/set lookup |
| `O(log n)` | Logarithmic | Each step halves what's left | +1 step | Binary search in a sorted list |
| `O(n)` | Linear | Touch each item once | 2× work | Summing a column, one loop |
| `O(n log n)` | Linearithmic | A good general sort | ~2.1× work | `sorted()`, `df.sort_values()` |
| `O(n²)` | Quadratic | Nested loop over the same data | 4× work | Comparing every pair of rows |

Two more worth knowing by name: `O(2ⁿ)` (exponential — naive recursive Fibonacci, brute-forcing
combinations; avoid) and `O(n!)` (factorial — trying every ordering; only tiny `n`).

### O(1) — constant

```python
def latest_price(prices: list[float]) -> float:
    return prices[-1]          # one indexing op, whatever len(prices) is
```

Dictionary and set lookups are ~O(1) too — that's *why* the "have I seen this before?"
trick below turns an O(n²) scan into O(n).

### O(log n) — logarithmic

```python
def binary_search(sorted_prices, target):
    lo, hi = 0, len(sorted_prices) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_prices[mid] == target:
            return mid
        if sorted_prices[mid] < target:
            lo = mid + 1       # throw away the lower half
        else:
            hi = mid - 1       # throw away the upper half
    return -1
```

A million sorted items? At most ~20 comparisons (`log₂(1_000_000) ≈ 20`). The catch: the
input **must be sorted** — that precondition is the whole trick.

### O(n) — linear

```python
def total_volume(volumes: list[int]) -> int:
    running = 0
    for v in volumes:          # one pass over n elements
        running += v
    return running
```

### O(n log n) — linearithmic

```python
returns_sorted = sorted(returns)   # Python's Timsort: O(n log n)
```

This is the floor for any comparison-based sort. When you see `.sort_values()` or
`sorted()`, this is the cost you're paying.

### O(n²) — quadratic (the trap)

```python
def any_duplicate_slow(prices):        # O(n^2): a loop inside a loop
    n = len(prices)
    for i in range(n):
        for j in range(i + 1, n):
            if prices[i] == prices[j]:
                return True
    return False

def any_duplicate_fast(prices):        # O(n): one pass + O(1) set lookups
    seen = set()
    for p in prices:
        if p in seen:
            return True
        seen.add(p)
    return False
```

Same question, two complexity classes. On 10,000 unique items the quadratic version takes
~1,900 ms; the linear one ~2 ms. Run `big_o_examples.py` and see it for yourself.

## How to spot the complexity of code you're reading

- **One loop over the input** → `O(n)`.
- **A loop inside a loop, both over the input** → `O(n²)`. (A loop over a *fixed* small
  thing, like 12 months, doesn't count — that's a constant.)
- **Halving the problem each step** (`mid = (lo+hi)//2`, divide-and-conquer) → `O(log n)`
  or `O(n log n)` if there's a pass at each level.
- **A dict/set lookup** → treat as `O(1)`; reaching for one is often how you kill an `O(n²)`.
- **Calling a sort** → `O(n log n)`; it usually dominates surrounding linear work.
- **Nested pandas `.apply` / a Python loop over `df.iterrows()`** → almost always the slow
  path. Vectorize instead (this is the Lesson 4 lesson, restated in Big O terms).

Report the **worst case** unless asked otherwise, and keep only the dominant term:
`O(n) + O(n²)` is just `O(n²)`; `O(2n)` is just `O(n)`.

## Recognition exercises

Decide the time complexity of each. Answers are at the bottom — try before peeking.

1. ```python
   def portfolio_value(holdings, prices):        # both are lists of length n
       total = 0
       for i in range(len(holdings)):
           total += holdings[i] * prices[i]
       return total
   ```

2. ```python
   def has_pair_summing_to(returns, target):
       for a in returns:
           for b in returns:
               if a + b == target:
                   return True
       return False
   ```

3. ```python
   def contains(sorted_prices, x):
       lo, hi = 0, len(sorted_prices) - 1
       while lo <= hi:
           mid = (lo + hi) // 2
           if sorted_prices[mid] == x:
               return True
           elif sorted_prices[mid] < x:
               lo = mid + 1
           else:
               hi = mid - 1
       return False
   ```

4. ```python
   def first_ticker(tickers):
       return tickers[0]
   ```

5. ```python
   def rank_by_return(returns):
       return sorted(returns, reverse=True)
   ```

6. ```python
   def build_price_lookup(symbols, prices):      # n symbols
       lookup = {}
       for sym, px in zip(symbols, prices):
           lookup[sym] = px                       # dict insert ~ O(1)
       return lookup
   ```

7. ```python
   def duplicate_dates(dates):                    # n dates
       seen = set()
       for d in dates:
           if d in seen:
               return True
           seen.add(d)
       return False
   ```

8. ```python
   def months_in_a_year_report(returns):          # returns has n days
       summary = []
       for month in range(12):                    # always 12
           summary.append(sum(returns))           # sum is O(n)
       return summary
   ```

### Answers

1. **O(n)** — a single loop over `n` elements.
2. **O(n²)** — a loop nested inside a loop, both over `returns`. (A hash set would make it O(n).)
3. **O(log n)** — binary search: each step halves the range.
4. **O(1)** — one indexing operation, independent of length.
5. **O(n log n)** — it's a sort.
6. **O(n)** — one pass, with an O(1) dict insert each time.
7. **O(n)** — one pass; the set lookup/insert is O(1), *not* another loop.
8. **O(n)** — the outer loop runs a *constant* 12 times, and each does O(n) work:
   `12 × O(n) = O(n)`. Constants drop out. (Watch for this: a fixed-count loop is not `O(n²)`.)

## Further reading

- *Grokking Algorithms* by Aditya Bhargava — the friendliest illustrated intro.
- Big-O Cheat Sheet: <https://www.bigocheatsheet.com/> — complexity of common operations and data structures.
- Python's own data-structure costs: <https://wiki.python.org/moin/TimeComplexity>
- **Practice with Claude:** paste any function and ask *"What's the time complexity of this and
  why? Can it be improved?"* — then check the reasoning against this page.
