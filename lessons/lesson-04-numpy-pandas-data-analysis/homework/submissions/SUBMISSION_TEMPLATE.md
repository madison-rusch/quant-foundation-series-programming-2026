# Homework Submission Template — Lesson 4

Use this format when submitting your homework via Pull Request (PR).

## Branch name

```bash
git checkout -b lesson4/<your-name>
```

**Example:** `lesson4/alice-chen` or `lesson4/bob-martinez`

## PR title

```
homework: <your-name> extend analysis
```

## PR description

Your PR description should answer **four things**:

### 1. What calculation did you add, and what was your plan?

Describe the extra calculation or comparison you chose and why it's interesting.

**Example:**
> I added a 5-day rolling volatility of the 10Y yield (rolling standard deviation), because I wanted
> to see whether the market got calmer or noisier over the window.

### 2. Stakeholder summary (3–5 sentences, plain English)

Explain what your analysis shows as if presenting to a non-technical stakeholder — no jargon.

**Example:**
> Over these three weeks, short-term interest rates stayed above long-term rates the whole time,
> which is unusual and often read as a caution signal about the economy. The 10-year rate drifted
> down toward the end of the period. Day-to-day moves were small — under one percent — so nothing
> dramatic happened, just a steady easing in the long rate.

### 3. Where AI helped and where you intervened

**Example:**
> AI helped me get the rolling-std syntax right and suggested labeling the chart's second axis.
> I intervened when it rounded mid-calculation — I moved the rounding to the print statement so the
> numbers stayed exact until display.

### 4. What did you learn reviewing the code?

Note anything you had to look up, question, or sanity-check.

## What to submit

In [this folder](.), add:

1. **Your analysis script** — `<your-name>_analysis.py`.
2. **Your updated chart** — `<your-name>_chart.png`.
3. **Your stakeholder summary** — in the PR description, following point 2 above.

## Commits

```bash
git add lessons/lesson-04-numpy-pandas-data-analysis/homework/submissions/
git commit -m "homework: <your-name> extend analysis"
git push origin lesson4/<your-name>
```

## Opening the PR

1. Go to https://github.com/madison-rusch/quant-foundation-series-programming-2026
2. Click **"Pull requests"** → **"New pull request"**
3. Set base to `main`, compare to `lesson4/<your-name>`
4. Paste your description (answering the four points above)
5. Click **"Create pull request"**

Your instructor will review and provide feedback!
