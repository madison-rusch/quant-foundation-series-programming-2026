# Demo 7 — Code: the Live Analysis

The heart of the lesson — roughly 40 minutes. Build the analysis live with the class using
plan/code/review. AI writes the code; the class reads every line, spots issues, and directs
decisions. **Don't rush** — pause at each step to ask the questions in the tables below.

The three scripts run as a pipeline: **fetch → analyze → plot.**

```bash
# from the repo root
cd lessons/lesson-05-equity-analysis-capstone/demos/07-code-live-analysis

python fetch_index.py     # 1. pull ~1yr of S&P 500 daily prices  -> index_prices.csv
python analyze_index.py   # 2. clean + compute returns/vol/drawdown -> prints headline numbers
python plot_index.py      # 3. the "clean chart"                   -> index_analysis.png
```

`analyze_index.py` and `plot_index.py` fall back to the committed `backup_sp500_1y.csv`
if `fetch_index.py` hasn't run (or the live pull failed) — so the analysis half never gets
blocked on a network hiccup. **That's the backup plan from the lesson notes, working automatically.**

## Expected output

`analyze_index.py` prints headline numbers and the most volatile stretch; `plot_index.py` prints
`Saved chart to index_analysis.png`. Open the PNG: S&P 500 close with its 50-day trend on top,
drawdown shaded below. (Exact numbers depend on when you pull; the backup CSV runs 2025-07 → 2026-07.)

## The scenario-brief checklist — does the output answer it?

| The manager asked for… | Where it is |
|---|---|
| The trend | 50-day rolling mean, the dashed line on the chart |
| Notable periods of volatility | Rolling annualized vol + the shaded drawdown panel; printed "most volatile stretch" |
| A clean chart for a presentation | `index_analysis.png` — labelled axes, title, legend |

## Pause-and-ask moments

Work these in as you build each file — this is where the learning happens.

### fetch_index.py
| Line / idea | Ask the class |
|---|---|
| `HEADERS = {"User-Agent": ...}` | Why does Yahoo need this? (blocks non-browser-looking requests) |
| `except requests.RequestException:` → `sys.exit(...)` | What could go wrong on the network, and what should the user see? |
| `if close is None: continue` | Why are there null rows in the data at all? (holidays / non-trading days) |
| `round(..., 2)` at write time | Why round here and *not* during the later calculations? |

### analyze_index.py
| Line / idea | Ask the class |
|---|---|
| `if df["close"].isna().any(): raise` | "Missing data is a decision, not a default" — why fail instead of guess here? |
| `pct_change()` | Simple vs log returns — which did we choose, and why does it matter? |
| `.rolling(VOL_WINDOW).std() * np.sqrt(TRADING_DAYS)` | Why `√252`? Why not `×252`? (variance scales with time; vol with its root) |
| `df["close"].cummax()` then `close / peak - 1` | What does drawdown capture that volatility doesn't? |
| `:.2%` formatting in `main()` | Rounding only at the display boundary — where did the raw precision live until now? |

### plot_index.py
| Line / idea | Ask the class |
|---|---|
| `matplotlib.use("Agg")` | Why a headless backend in class? (save to file, don't block on a window) |
| `from analyze_index import add_analysis, ...` | Why import the analysis instead of copy-pasting it? (one source of truth) |
| `ax.legend()` / `set_title` / `set_ylabel` | What makes this chart something you'd actually put on a slide? |

## "How would you explain this to your manager?"

Ask it repeatedly. The answer to the brief in one breath:
*"The S&P 500 rose over the year with a clear upward trend. There was one sharp, volatile drawdown of
about 9% in the spring before it recovered to new highs. Here's the chart — level and trend on top,
the drawdown shaded below."*

## Talking points

- This is the whole course in one pipeline: scrape/pull (L3) → clean → analyze (L4) → visualize,
  built with plan/code/review (L2) in the tools from L1.
- Let students catch the mistakes. If Claude writes something subtly off (a look-ahead in a rolling
  calc, the wrong annualization), *that's the lesson* — Review is where you earn your salary.
- Keep tying every number back to the brief. Code that runs is not the goal; code that answers the
  manager's question is.
