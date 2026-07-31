# Homework Submission Template — Lesson 5 (optional)

Use this format if you submit an optional capstone extension via Pull Request (PR).

## Branch name

```bash
git checkout -b lesson5/<your-name>
```

**Example:** `lesson5/alice-chen`

## PR title

```
lesson5: <your-name> index analysis
```

## PR description

Answer **four things**:

### 1. What did you analyze, and what was your plan?

Which index/period, and what calculation(s) you added beyond the in-class version.

**Example:**
> I ran the pipeline on the FTSE 100 over the last two years and added a 60-day EWMA volatility
> alongside the simple rolling vol, to see how the two respond differently to a shock.

### 2. Stakeholder summary (3–5 sentences, plain English)

What your analysis shows, as if presenting to a non-technical manager — no jargon.

### 3. Where AI helped and where you intervened

**Example:**
> Claude adapted the fetch script to the new symbol quickly. I intervened on the EWMA span — its
> first guess didn't match the window I wanted, and I corrected the annualization.

### 4. What did you learn reviewing the code?

Anything you had to look up, question, or sanity-check against a known value.

## What to submit

In [this folder](.), add:

1. **Your analysis script** — `<your-name>_analysis.py`.
2. **Your chart** — `<your-name>_chart.png`.
3. **Your stakeholder summary** — in the PR description (point 2 above).

## Commits

```bash
git add lessons/lesson-05-equity-analysis-capstone/homework/submissions/
git commit -m "lesson5: <your-name> index analysis"
git push origin lesson5/<your-name>
```

## Opening the PR

1. Go to https://github.com/madison-rusch/quant-foundation-series-programming-2026
2. **Pull requests** → **New pull request**
3. Base `main`, compare `lesson5/<your-name>`
4. Paste your description (the four points above)
5. **Create pull request**

Your instructor will review and provide feedback!
