# quant-foundation-series-programming-2026

Repository for the UChicago Quant Foundations Programming Module — Summer 2026.

## Getting started

```bash
git clone https://github.com/madison-rusch/quant-foundation-series-programming-2026.git
cd quant-foundation-series-programming-2026
```

Then create your virtual environment — in VS Code, `Ctrl+Shift+P` → **Python: Create Environment** → **Venv**,
and check `requirements.txt` when prompted. Or from a terminal:

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## Lessons

| # | Topic | |
|---|---|---|
| 1 | Developer Environment & Git | [lessons/lesson-01-dev-environment-git/](lessons/lesson-01-dev-environment-git/) |
| 2 | AI as a Coding Tool | [lessons/lesson-02-ai-coding-tool/](lessons/lesson-02-ai-coding-tool/) |
| 3 | Python Fundamentals via Web Scraping | [lessons/lesson-03-python-fundamentals/](lessons/lesson-03-python-fundamentals/) |
| 4 | NumPy, Pandas & Data Analysis | [lessons/lesson-04-numpy-pandas-data-analysis/](lessons/lesson-04-numpy-pandas-data-analysis/) |
| 5 | Student-Driven Session | _coming soon_ |

## How we work

- **Never commit to `main` directly.** Branch, commit, push, open a Pull Request.
- **Log questions as GitHub Issues.** Anything confusing, anything you want revisited — no question is too small.
  Issues are reviewed before every lesson and directly shape the student-driven block in Lesson 5.
- **`.venv/` is not committed.** `requirements.txt` is the shared recipe; each of us builds our own environment from it.
