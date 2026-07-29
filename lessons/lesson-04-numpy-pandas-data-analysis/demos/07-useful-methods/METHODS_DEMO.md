# Demo 7 — Useful Pandas methods

Optional / overflow demo, roughly 15 minutes. Demos 2–3 covered the core verbs (filter, groupby,
`pct_change`, `rolling`). This is a grab-bag of methods that show up constantly in real analysis but
didn't fit earlier — each framed on financial data so the class sees *why* you'd reach for it.

`useful_methods.py` is the artifact. It uses the bundled yield series and the Lesson 3 constituents CSV,
both of which run standalone.

## Run it

```bash
python lessons/lesson-04-numpy-pandas-data-analysis/demos/07-useful-methods/useful_methods.py
```

Expected output (abridged):

```
--- describe() and value_counts() ---
ticker length summary:
count    503.00
mean       3.20
...
top 5 sectors by company count:
sector
Industrials               81
Financials                76
Information Technology    74
...

--- shift(), diff(), and cumulative returns ---
            us_10y  abs_change_bps  growth_index
date
2026-06-15    4.49             3.0        1.0158
...
2026-06-19    4.39            -2.0        0.9932

--- np.where() and clip() ---
            us_10y regime  us_10y_capped
2026-06-02    4.45   high           4.45
...

--- pd.cut() for bucketing ---
 us_10y bucket
   4.42    mid
   4.47   high
   4.39    low
...

--- .dt accessor and resample() ---
weekly max 10y yield:
2026-06-07    4.47
2026-06-14    4.46
2026-06-21    4.49
```

## The methods

| Method | What it does | When you reach for it |
|---|---|---|
| `describe()` | One-line stats summary of numeric columns | First look at any new numeric data |
| `value_counts()` | Frequency table of a categorical column | "What's the mix of sectors/ratings?" |
| `shift(1)` | Yesterday's value, aligned to today's row | Any period-over-period calculation |
| `diff()` | Row-to-row change (`x - x.shift(1)`) | Daily moves, first differences |
| `cumprod()` | Running product | Compounding returns into a growth curve |
| `np.where(cond, a, b)` | Vectorized if/else | Labelling / flagging rows without a loop |
| `clip(lo, hi)` | Cap values into a range | Winsorizing outliers before stats |
| `pd.cut(x, bins)` | Bin a continuous column into labeled ranges | Buckets, tiers, ratings |
| `.dt` accessor | Pull calendar parts out of datetimes | Grouping by weekday/month |
| `resample("W")` | Regroup a time series by calendar period | Daily → weekly/monthly aggregation |

## Review

| Code | Question to ask the class |
|---|---|
| `(1 + returns).cumprod()` | Why do we add 1 before compounding, and what does a value below 1.0 mean? (a cumulative loss) |
| `np.where(df["us_10y"] >= 4.45, "high", "low")` | How is this different from writing a `for` loop with an `if`? (vectorized, no loop) |
| `df["us_10y"].clip(upper=4.47)` | What happened to the 4.49 value? (capped at 4.47 — a deliberate distortion) |
| `resample("W").max()` | Why does the index change from daily dates to week-ending dates? |

## Talking points

- `shift`/`diff`/`cumprod` are the time-series trio: look back one step, take the change, compound it.
  Nearly every return calculation is built from these.
- `np.where` and `clip` reinforce **vectorization** — both replace a row loop with one array operation.
- `pd.cut` and `resample` are how you go from raw rows to *buckets* and *periods* — the shapes
  stakeholders actually ask for ("group by rating", "give me weekly numbers").
- None of these are exotic; they're the everyday vocabulary that separates fluent Pandas from
  loop-everything Pandas. Pair with Demo 6 so the class sees both the sharp edges and the power tools.
