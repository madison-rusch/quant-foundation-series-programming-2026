# Lesson 3 Homework — Extend the Scraper

Due before Lesson 4. Your instructor will review every PR.

## What you're doing

Take the in-class scraper and **extend it to pull at least one more data point**, then save the
result cleanly to a CSV. That CSV is your input for Lesson 4 — keep it.

## Steps

```bash
# 1. Start from the latest main
git checkout main
git pull

# 2. Create your own branch
git checkout -b lesson3/<your-name>

# 3. Plan: write down what extra data point you'll add and where it lives on the page

# 4. Code: prompt Claude (plan/code/review) to extend the scraper

# 5. Review: read every line. Add at least one try/except and explain why it's there.

# 6. Run it, confirm the CSV looks right, then commit and push
git add lessons/lesson-03-python-fundamentals/homework/submissions/
git commit -m "homework: <your-name> extend scraper"
git push origin lesson3/<your-name>
```

Then open a **Pull Request** back to `main`.

## Requirements

1. **Extend the scraper** — pull at least one additional column beyond the in-class version
   (e.g. headquarters location, or scrape a second table).
2. **Save a clean CSV** — no blank rows, sensible headers. Name it `<your-name>_data.csv` and put it
   in [submissions/](submissions/). **You need this CSV for Lesson 4.**
3. **Plain-English explanation** — 3–5 sentences describing what your scraper does, as if explaining
   it in an interview.
4. **AI notes** — call out at least **2 places AI helped** and **1 place you had to intervene or
   correct it**. See [SUBMISSION_TEMPLATE.md](submissions/SUBMISSION_TEMPLATE.md).

## If your scraper won't cooperate

Sites change and networks fail — that's the lesson, not a personal failing. A backup CSV is provided
in [scripts/backup_sp500.csv](scripts/backup_sp500.csv) so you can still complete Lesson 4. If you
use it, say so in your PR and describe what went wrong with your live scrape.

## Rules

- Use Claude Code, but **read and understand every line** before submitting.
- Stuck for more than 30 minutes? **Open a GitHub Issue.** That's the process, not giving up.
