# Interview Question Bank

A mix of technical Python and financial-mathematics domain questions, drawn from the whole course.
Each has a suggested **answer framework** — the shape of a strong answer, not a script to memorize.
The best answers pair a one-sentence definition with a concrete example, ideally from something you
actually built in this course (the equity-index analysis, the S&P 500 scraper, the yield-curve work).

> **How to use this:** don't read the answers first. Cover them, attempt each out loud, *then* check.
> Better still, hand the whole bank to Claude and run a live mock — see the bottom of this page.

## Part 1 — Python & tooling

**1. What's the difference between a NumPy array and a Python list?**
An array is homogeneously typed and fixed-size, so operations vectorize and run in compiled C —
fast and memory-compact. A list holds mixed types and grows dynamically. *Example:* "For the index
returns I used arrays so `prices.pct_change()` runs as one vectorized op instead of a Python loop."

**2. What is a pandas DataFrame and when would you use one?**
A 2-D table with labelled rows (an index) and columns, each column a typed Series. Use it for
tabular or time-series data — loading, cleaning, filtering, grouping, analysis. *Example:* "I loaded
a year of S&P 500 closes indexed by date, then computed rolling volatility with `.rolling()`."

**3. How do you handle missing data in pandas?**
Detect it (`isna()`), then decide *explicitly*: drop (`dropna`), fill (`fillna`/`ffill`), or fail
loudly. The point is that it's a decision, not a default — a silent NaN corrupts every calculation
downstream. *Example:* "For a missing yield I carried the prior day forward with `ffill`, because a
non-trading day isn't a zero."

**4. What is vectorization and why is it faster than a loop?**
Applying an operation to a whole array at once, executed in compiled code, instead of a Python-level
loop over elements. Faster *and* clearer. In Big O terms it's the same `O(n)` work, but with a
dramatically smaller constant factor — plus no per-iteration interpreter overhead.

**5. Explain time complexity / Big O in one sentence, then give an example of improving it.**
Big O is how work grows as input grows. *Example:* "Checking for duplicate dates with a nested loop
is `O(n²)`; using a `set` for membership makes it `O(n)` — same answer, orders of magnitude faster
on large data." (See [big-o-notation.md](../01-big-o-notation/big-o-notation.md).)

**6. List comprehension vs generator expression?**
List (`[...]`) builds the whole thing in memory now; generator (`(...)`) yields lazily, one item at
a time, near-constant memory. Use a generator for large or streamed data you pass through once.

**7. What is a decorator?**
A function that wraps another to add behaviour (timing, caching, logging) without changing its body;
`@lru_cache` is the one I reach for most. (See [python-keywords-and-patterns.md](../03-python-keywords-patterns/python-keywords-and-patterns.md).)

**8. Why `float` for returns but not for a cash ledger?**
Returns and prices in analytics tolerate tiny rounding error and need speed, so `float` is fine.
Exact money — settlement, balances — must use `decimal.Decimal`, because `0.1 + 0.2 != 0.3` in
binary floating point and those errors accumulate. Round only at the display/settlement boundary.

**9. What's the difference between `git merge` and a pull request?**
`merge` combines branches locally. A pull request is a *review gate* on top of a merge: it proposes
the change, runs checks, and lets a human read the diff before it lands on `main`. "Never commit to
`main` directly" is the whole reason PRs exist.

**10. How do you approach debugging code that runs but gives a wrong answer?**
Reproduce it, isolate the smallest failing case, then inspect intermediate values — print or a
breakpoint and the debugger's variable view. Check assumptions at the boundaries (first/last row,
NaNs, off-by-one, look-ahead). A test that captures the bug prevents its return.

## Part 2 — Financial mathematics & domain

**11. Explain a rolling average to a non-technical stakeholder.**
"Instead of one noisy daily number, we average the last N days and slide that window forward. It
smooths out the day-to-day jitter so the underlying trend is visible — like squinting at a chart."

**12. What is volatility and how did you measure it?**
Volatility is how much returns vary — the standard deviation of returns. I computed the std of daily
returns over a rolling window and annualized it by multiplying by `√252` (trading days per year),
because variance scales linearly with time, so standard deviation scales with the square root.

**13. Why annualize with √252 for volatility but ×252 for returns?**
Returns compound/add linearly over time, so they scale by the number of periods. Variance adds
linearly, and volatility is the *square root* of variance — so it scales by the square root of the
number of periods. Hence `√252`.

**14. Simple returns vs log returns — when would you use each?**
Simple returns (`P_t/P_{t-1} − 1`) are additive *across assets*, so they're natural for portfolio
aggregation. Log returns (`ln(P_t/P_{t-1})`) are additive *across time*, which makes multi-period
compounding and much statistical modelling cleaner. Pick deliberately and say which you used.

**15. What is a maximum drawdown and why does it matter?**
The largest peak-to-trough decline over a period — how far below its running high-water mark an
investment fell. It captures downside pain in a way volatility doesn't: two strategies can share a
volatility number but have very different worst-case losses.

**16. Your analysis produced an unexpected result. What do you check?**
Data first: right symbol, right date range, correct time zone, missing days, splits/adjustments,
duplicate rows. Then the method: look-ahead bias (using future data in a signal), a cherry-picked
window, survivorship bias, an off-by-one in a shift/rolling calc. Then sanity-check magnitudes
against a known reference. Don't trust a number just because the code ran.

**17. How would you explain the yield curve, and what does an inverted curve suggest?**
The yield curve plots interest rates against maturity. Normally longer maturities yield more. When
short rates sit *above* long rates the curve is inverted — historically a recession warning, as it
implies the market expects rates (and growth) to fall.

**18. What is the time value of money?**
A dollar today is worth more than a dollar tomorrow, because today's dollar can be invested to earn
a return. Present value discounts future cash flows back at a rate; future value compounds them
forward. Everything in fixed income and derivatives pricing is built on this.

**19. How did you decide which data source to use for the index analysis?**
Criteria: does it have the history I need, is it reliable and free, is the format clean, and can I
reproduce the pull? I used the Yahoo Finance chart endpoint (no key, returns JSON), and committed a
backup CSV so the analysis is reproducible even if the live pull fails. Trade-offs, stated out loud.

**20. Walk me through what your script does. (The big one.)**
Structure it as a pipeline: *"It pulls a year of daily index prices, loads them into a DataFrame and
checks for missing data, then computes daily returns, a rolling trend, annualized rolling volatility,
and drawdown. Finally it prints headline numbers and saves a two-panel chart — price-with-trend on
top, drawdown shaded below — that answers the brief: the trend, the volatile periods, and a clean
visual."* Lead with the goal, then the steps, then the output.

## Answer frameworks that work everywhere

- **Definition → example → trade-off.** One sentence of what it is, one concrete example (ideally
  from your own work), one line on when *not* to use it. This shape signals real understanding.
- **For "walk me through" questions:** goal first, then the steps as a pipeline, then the output.
  Don't narrate line by line — narrate the *shape*.
- **When you don't know:** say what you'd do to find out. "I haven't used that, but I'd expect it to
  work like X because Y, and I'd confirm in the docs." Honesty plus a method beats a bluff.
- **Tie it back to a decision.** "Missing data is a decision, not a default." "float for analytics,
  Decimal for money." Sentences like these show you understand *why*, not just *how*.

## Practising with Claude

Paste this into Claude Code and run a full mock:

```
Act as an interviewer for an entry-level quantitative / data-analyst role. Ask me ONE question at a
time, drawn from Python fundamentals, pandas/NumPy, Big O, and financial-maths topics (returns,
volatility, drawdown, yield curves, time value of money). Wait for my answer, then give me brief
feedback and ONE harder follow-up based on what I said before moving on. Don't hand me the answer
up front. After 8 questions, give me structured written feedback: strengths, weaknesses, and the two
things to study next.
```

Then answer *out loud* as if in a real interview — the goal is fluency, not a written essay.
