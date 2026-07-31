# Lesson 5 — Optional Extensions

**No formal homework — the course is complete.** These are optional ways to keep building. If you do
one, open a PR the same way you have all term; your instructor is happy to review it.

## Option A — Repeat the analysis on a different index or period

Take the in-class pipeline ([../demos/07-code-live-analysis/](../demos/07-code-live-analysis/)) and
point it at a different market or window:

- A different index: FTSE 100 (`^FTSE`), Nasdaq 100 (`^NDX`), Nikkei 225 (`^N225`), Euro Stoxx 50
  (`^STOXX50E`) — just change the `SYMBOL` in `fetch_index.py`.
- A different period: the last 3 years, or a specific stressed window.
- Add at least one new calculation: a second rolling window, EWMA volatility, rolling Sharpe, or a
  comparison against a second index on the same chart.

Then write a 3–5 sentence plain-English stakeholder summary of what your analysis shows.

## Option B — Run a full mock interview

Use the prompt from [../demos/09-mock-interview/](../demos/09-mock-interview/) (or the bank in
[../demos/04-interview-question-bank/](../demos/04-interview-question-bank/)) and have Claude run a
mock covering all five lessons. Ask for **structured written feedback** at the end, then note the two
things you'll study next. No submission needed — this one's just for you.

## Option C — Work through the first-half references

Revisit [Big O](../demos/01-big-o-notation/), [algorithms](../demos/02-algorithms/), and
[Python patterns](../demos/03-python-keywords-patterns/) at your own pace before your masters starts.
Run each script, do the recognition exercises, and quiz yourself with Claude.

## If you submit (Option A)

See [submissions/SUBMISSION_TEMPLATE.md](submissions/SUBMISSION_TEMPLATE.md) for the format — same
plan/code/review workflow, same PR steps as every lesson:

```bash
git checkout main && git pull
git checkout -b lesson5/<your-name>
# ... build, review every line, run it, check the chart ...
git add lessons/lesson-05-equity-analysis-capstone/homework/submissions/
git commit -m "lesson5: <your-name> index analysis"
git push origin lesson5/<your-name>
```

Then open a Pull Request back to `main`.
