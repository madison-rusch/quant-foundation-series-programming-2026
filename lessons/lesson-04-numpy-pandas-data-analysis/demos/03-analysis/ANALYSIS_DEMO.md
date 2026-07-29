# Demo 3 — Analysis with Pandas

Roughly 25 minutes. Run meaningful calculations on real financial data, keeping each step in a small
named function so the analysis stays clean and reusable. We switch to a bundled Treasury-yield time
series (`../02-pandas-dataframes/sample_rates.csv`) because the constituents list isn't a time series
and percentage change / rolling averages need one.

`analyze.py` is the artifact.

## Run it

```bash
python lessons/lesson-04-numpy-pandas-data-analysis/demos/03-analysis/analyze.py
```

Expected output:

```
last 5 days of analysis:
            us_2y  us_10y  us_10y_pct_change  us_10y_roll3  spread_2s10s
date
2026-06-15   4.87    4.49              0.673         4.460         -0.38
2026-06-16   4.85    4.48             -0.223         4.477         -0.37
2026-06-17   4.81    4.44             -0.893         4.470         -0.37
2026-06-18   4.78    4.41             -0.676         4.443         -0.37
2026-06-19   4.76    4.39             -0.454         4.413         -0.37

mean 10y yield:   4.431
biggest 1-day move: 0.893%
curve inverted (2y > 10y) every day? True
```

## Review

| Code | Question to ask the class |
|---|---|
| `df["us_2y"].ffill()` | The CSV has one missing 2y value — what did we decide to do with it, and why is that a *choice*? |
| `df["us_10y"].pct_change() * 100` | What does `pct_change` compare each row to? (the row before it) |
| `df["us_10y"].rolling(3).mean()` | Why are the first two rolling values NaN? |
| `df["us_10y"] - df["us_2y"]` | The spread is negative every day — what does 2y > 10y mean? (an **inverted yield curve**) |

The inverted curve is a real finance talking point: short rates above long rates is historically a
recession signal. The class just *found* that in the data, which is the point of analysis.

## Float precision, revisited

These yields are **analytics**, so `float` is fine — but notice we round only at the display boundary
(`{:.3f}`), never mid-calculation. Same discipline as Lesson 3: round late, and never `==` two floats.
Contrast with money you *settle*, where you'd reach for `Decimal`.

## Talking points

- Small named functions (`load_rates`, `add_analysis`) keep analysis readable and reusable — this is
  the plan/code/review habit applied to your own code, not just AI's.
- `pct_change` and `rolling` are the two verbs that turn a price series into an analysis. Everything
  else builds on them.
- Always ask "does this number make sense?" — the inverted-curve finding is a sanity check that
  passed. That reasoning is part of Review.
