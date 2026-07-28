# Homework Submission Template — Lesson 3

Use this format when submitting your homework via Pull Request (PR).

## Branch name

```bash
git checkout -b lesson3/<your-name>
```

**Example:** `lesson3/alice-chen` or `lesson3/bob-martinez`

## PR title

```
homework: <your-name> extend scraper
```

## PR description

Your PR description should answer **four things**:

### 1. What extra data point did you add, and what was your plan?

Describe what you decided to pull beyond the in-class version, and where it lived on the page.

**Example:**
> I added the headquarters location column. I found it in the same constituents table, so I just
> pulled one more cell per row.

### 2. Plain-English explanation of your scraper (3–5 sentences)

Explain what your scraper does as if in an interview.

**Example:**
> My script downloads the S&P 500 Wikipedia page, finds the constituents table, and reads each row
> into a record with the ticker, company name, sector, date added, and headquarters. It wraps the
> download and the parse in error handling so a failed request gives a clear message instead of
> crashing. Finally it writes everything to a CSV I can load in Lesson 4.

### 3. Where AI helped (at least 2) and where you intervened (at least 1)

**Example:**
> AI helped: (1) it knew Wikipedia needs a User-Agent header, which I'd never have guessed;
> (2) it suggested `raise_for_status()` to catch bad HTTP responses.
> I intervened: Claude first grabbed the wrong column index for headquarters — I had to inspect the
> table in the browser and correct the index.

### 4. What did you learn reviewing the code?

Note anything you had to look up, question, or push back on.

## What to submit

In [this folder](.), add:

1. **Your extended scraper** — `<your-name>_scraper.py`, with at least one `try/except` and a
   comment explaining why it's there.
2. **Your cleaned data** — `<your-name>_data.csv`. **Keep this — Lesson 4 uses it.**
3. **Your prompt notes** — in the PR description, following the four points above.

## Commits

```bash
git add lessons/lesson-03-python-fundamentals/homework/submissions/
git commit -m "homework: <your-name> extend scraper"
git push origin lesson3/<your-name>
```

## Opening the PR

1. Go to https://github.com/madison-rusch/quant-foundation-series-programming-2026
2. Click **"Pull requests"** → **"New pull request"**
3. Set base to `main`, compare to `lesson3/<your-name>`
4. Paste your description (answering the four points above)
5. Click **"Create pull request"**

Your instructor will review and provide feedback!
