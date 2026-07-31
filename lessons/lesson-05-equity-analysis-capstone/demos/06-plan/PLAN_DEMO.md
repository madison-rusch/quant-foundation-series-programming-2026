# Demo 6 — Plan

Roughly 10 minutes. This is the **Plan** step of plan/code/review, done out loud as a class before
any code exists. Shape the plan live from student input — you're modelling how to scope an ambiguous
brief, not reading a prepared answer.

## Do it live

Open Claude Code and ask the class to help you fill in a plan. A prompt that works:

```
I've joined a quant team. My manager wants a quick analysis of how the S&P 500 performed over the
past year: the trend, any notable volatile periods, and a clean chart for a presentation. Before we
write any code, help me PLAN. Ask me what I want for the data source, the calculations, and the final
output — one decision at a time. Don't write code yet.
```

Let the class answer each decision. Steer toward — but let *them* reach — something like the plan below.

## The plan we're aiming for

**Data**
- Source: Yahoo Finance chart endpoint (no API key, returns JSON, reproducible). Symbol `^GSPC`.
- Range: trailing ~13 months of daily closes (a little over a year so rolling windows warm up).
- **Backup:** a committed CSV, in case the live pull fails in class — decided up front, not improvised.

**Clean**
- Parse dates, sort ascending, set the date as the index.
- Missing closes: fail loudly rather than silently analyze a hole (it's a decision, not a default).

**Calculate**
- Daily simple returns (`pct_change`).
- Trend: a 50-day rolling mean of the close.
- Volatility: rolling std of daily returns, annualized by `√252` — the "notable periods" answer.
- Drawdown: distance below the running peak — the downside view volatility alone misses.
- Headline numbers: total return, annualized vol, best/worst day, max drawdown.

**Output**
- Printed headline numbers for the manager.
- A two-panel chart: price + trend on top, drawdown shaded below. Labelled, titled, saved as PNG.

## Map it to the files we'll build

| Plan step | File (in [../07-code-live-analysis/](../07-code-live-analysis/)) |
|---|---|
| Pull + backup | `fetch_index.py` (+ committed `backup_sp500_1y.csv`) |
| Clean + calculate | `analyze_index.py` |
| Chart | `plot_index.py` |

## Talking points

- Writing the plan down first is what stops AI from confidently building the *wrong* thing fast.
- Naming the backup data source *in the plan* is the professional move — the lesson plan calls for it
  because live scraping fails at the worst moment.
- Notice every vague word from the brief now has a concrete definition: "trend" = 50-day mean,
  "volatile periods" = rolling annualized vol + drawdown. That translation is the real work.
