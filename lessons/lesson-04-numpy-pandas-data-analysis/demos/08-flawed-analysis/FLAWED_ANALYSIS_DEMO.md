# Demo 8 — When the analysis is wrong but the code isn't

Optional / overflow demo, roughly 15 minutes. Demo 6 was about bugs that crash or silently corrupt a
*value*. This one has none of that — every line runs cleanly, no exceptions, no NaN. The problem is the
**conclusion**: a plausible-sounding takeaway that the full data contradicts. This is what AI-generated
analysis looks like when it's wrong — it runs, it prints a tidy number, and Review has to catch the
reasoning error because the computer won't.

`flawed_analysis.py` is the artifact. It reuses the bundled yield series and the Lesson 3 constituents
CSV, both of which run standalone.

## Run it

```bash
python lessons/lesson-04-numpy-pandas-data-analysis/demos/08-flawed-analysis/flawed_analysis.py
```

Expected output:

```
--- 1. Cherry-picked window ---
last 3 days: 4.44 -> 4.39  (-0.05)
FLAWED CONCLUSION: '10y yield is trending down, expect further declines.'

full range:  4.42 -> 4.39  (-0.03)
peak was 4.49 on 2026-06-15
FULLER PICTURE: yields rose into that peak, and the last 3 days are just
easing back off it - a pullback inside a range, not a new downtrend.

--- 2. Look-ahead bias in a rolling signal ---
centered-average signal fires 'below trend' on 7 days
FLAWED CONCLUSION: 'this rule looks strong in the backtest, ship it.'

trailing-average signal (only past+today) fires on 7 days
the two signals disagree on 4 of the 15 days
e.g. on 2026-06-04, us_10y=4.44: the centered average 4.440 needed the NEXT row's yield to compute
FULLER PICTURE: center=True is fine for a retrospective chart, but as a
trading signal it peeks at data that wasn't available yet - the backtest
numbers are inflated by information the strategy could never have had.

--- 3. Survivorship bias in the constituents list ---
79 of today's 503 constituents were added before 1980
FLAWED CONCLUSION: 'companies added to the index before 1980 have a great long-run track record - buy old-guard names and hold.'

FULLER PICTURE: this dataset has no row for a company once it leaves the
index, so there's no way to compute how many pre-1980 additions failed -
the denominator for a 'success rate' isn't in the data at all. The 79 rows
above are the ones that happened to survive; nothing here measures the ones
that didn't.
```

## The three pitfalls

| # | Pitfall | Why it fools you | The fix |
|---|---|---|---|
| 1 | Cherry-picked window | The last 3 days *do* point down — that part is true. It's just not the whole story: the series peaked days ago and is only pulling back toward where it started | Always look at the full series before trusting a short window; ask "what does the window before this one show?" |
| 2 | Look-ahead bias | `rolling(3, center=True)` is a real, useful function — it's just the wrong one for a live signal, because it needs tomorrow's value to label today | For anything that becomes a trading rule, use a trailing window only; `center=True` is for retrospective charts |
| 3 | Survivorship bias | The row count is real and the query runs fine — the dataset just structurally can't answer the question being asked of it | Ask "what's missing from this data, not what's in it" before drawing a conclusion from a survivors-only list |

## Live debugging exercise

Run the script and, before scrolling to the "FULLER PICTURE" lines, have the class debug each
"FLAWED CONCLUSION" out loud:

1. What's the claim, in one sentence?
2. What computation produced it? Is the computation itself correct?
3. What's missing from the picture that would change the takeaway?

This mirrors Plan/Code/Review: the *code* passed review (it's correct Pandas), but the *analysis*
didn't — Review has to extend past "does this run" to "does this claim survive more data."

## Talking points

- This is the demo for "AI writes code that runs but reaches the wrong conclusion." It won't throw an
  exception, and it won't print NaN — the only way to catch it is to read the claim skeptically and ask
  what it's built on.
- Pitfall 1 is the most common one in the wild: a recency-weighted read of *any* series, given enough
  cherry-picking, can be made to say almost anything.
- Pitfall 2 connects to Demo 3/7's `rolling`/`shift` — the same window functions that are perfectly
  correct for descriptive stats become invalid the moment they're used to simulate a real-time decision.
- Pitfall 3 is a classic finance interview topic (ties to Demo 5) — "why do backtests on today's index
  membership overstate historical returns?" is exactly this bias.
- The meta-point: **"it ran without errors" is not the same as "the conclusion is right."** Review means
  questioning the claim, not just reading the code for bugs.
