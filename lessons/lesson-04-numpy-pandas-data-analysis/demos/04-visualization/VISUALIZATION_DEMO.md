# Demo 4 — Visualization

Roughly 20 minutes. Just enough matplotlib to produce one clear chart. This **closes the pipeline**:
scrape (L3) → clean → analyze → visualize. Build it plan/code/review — AI writes it, the class reads it.

`plot.py` is the artifact. It reuses the analysis functions from Demo 3 rather than re-deriving them,
and saves to PNG (headless `Agg` backend) so it runs in class without a blocking window.

## Run it

```bash
python lessons/lesson-04-numpy-pandas-data-analysis/demos/04-visualization/plot.py
```

Expected output:

```
Saved chart to yields.png
```

Open `yields.png` in the folder: the 2Y and 10Y yields over time, plus the 10Y's 3-day rolling
average as a dashed line.

## Review

| Line | Question to ask the class |
|---|---|
| `matplotlib.use("Agg")` | Why a headless backend? (save to file, don't block on a window) |
| `from analyze import add_analysis, load_rates` | Why import the analysis instead of copy-pasting it? |
| `ax.plot(..., label="2Y yield")` + `ax.legend()` | What makes a chart *readable* — what did we label? |
| `ax.set_xlabel / set_ylabel / set_title` | A chart with no axis labels is a quiz, not a result. |

## Discuss

Put the chart up and ask: *"What does this tell us? What decision could it inform?"*

- The 2Y sits above the 10Y the whole window — the inverted curve from Demo 3, now visible at a glance.
- The rolling average smooths the daily noise — you can see the 10Y trend down late in the window.
- A chart is how you hand analysis to someone who won't read your code. That's the homework's
  stakeholder summary in visual form.

## Talking points

- Minimum viable chart: a line, labeled axes, a title, a legend. That's 90% of the value.
- Reusing `analyze.py` instead of duplicating it is the clean-code point — one source of truth for
  the analysis, whether you print it or plot it.
- Make the scrape→clean→analyze→visualize arc explicit here — the class just built the whole pipeline
  across two lessons.
