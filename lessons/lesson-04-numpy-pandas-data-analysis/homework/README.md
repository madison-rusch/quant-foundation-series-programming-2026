# Lesson 4 Homework — Extend the Analysis

Due before Lesson 5. Your instructor will review every PR.

## What you're doing

Take the in-class analysis and **add at least one more calculation or comparison of your choice**,
update the visualization to reflect it, and write a short plain-English summary of what your analysis
shows — as if presenting to a non-technical stakeholder.

Use your own Lesson 3 data if you have it, or the bundled datasets
([sample_rates.csv](../demos/02-pandas-dataframes/sample_rates.csv) for a time series,
[backup_sp500.csv](../../lesson-03-python-fundamentals/homework/scripts/backup_sp500.csv) for the
constituents).

## Steps

```bash
# 1. Start from the latest main
git checkout main
git pull

# 2. Create your own branch
git checkout -b lesson4/<your-name>

# 3. Plan: write down the extra calculation you'll add and why it's interesting

# 4. Code: prompt Claude (plan/code/review) to add the calculation and update the chart

# 5. Review: read every line. Confirm your numbers make sense (does the result look right?)

# 6. Run it, check the chart, then commit and push
git add lessons/lesson-04-numpy-pandas-data-analysis/homework/submissions/
git commit -m "homework: <your-name> extend analysis"
git push origin lesson4/<your-name>
```

Then open a **Pull Request** back to `main`.

## Requirements

1. **One more calculation** — beyond the in-class version (e.g. a different rolling window, a
   volatility measure, a comparison across sectors, a max drawdown).
2. **Updated visualization** — the chart should reflect your new analysis. Save it as a PNG in
   [submissions/](submissions/).
3. **Stakeholder summary** — 3–5 sentences, plain English, no jargon. What does your analysis show
   and why would someone care?
4. **AI notes** — note where AI helped and where you had to intervene. See
   [SUBMISSION_TEMPLATE.md](submissions/SUBMISSION_TEMPLATE.md).

## Rules

- Use Claude Code, but **read and understand every line** before submitting.
- Reinforce float precision — watch for rounding issues; round only at the display boundary.
- Stuck for more than 30 minutes? **Open a GitHub Issue.**
