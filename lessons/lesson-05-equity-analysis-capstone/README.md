# Lesson 5 — Real-World Equity Analysis (Capstone)

2-hour live session, and the last of the course. Two halves:

1. **First half — the CS toolkit** you'll be quizzed on: Big O, common algorithms, and the Python
   keywords & patterns that come up in interviews and code review. Taught up front, then yours to
   keep as reference.
2. **Second half — work like a real quant team.** Take a deliberately vague brief, scope it, and
   build a full equity-index analysis end to end with plan/code/review — the whole course in one
   pipeline: **pull → clean → analyze → visualize.**

## Running order

| # | Topic | Time | Folder | What happens |
|---|---|---|---|---|
| Opening | Course review & GitHub issues | 15 min | — | Recap the course arc; work through 2–3 of the most common issues logged all term, live with Claude |
| **First half — the toolkit** | | | | |
| 1. | Big O notation | 15 min | [demos/01-big-o-notation/](demos/01-big-o-notation/) | The five complexity classes with runnable, timed examples; how to read the complexity of code; recognition exercises |
| 2. | Common algorithms | 10 min | [demos/02-algorithms/](demos/02-algorithms/) | Binary search, sorting, recursion & memoization — what they are, why they matter, self-checking code |
| 3. | Python keywords & patterns | 10 min | [demos/03-python-keywords-patterns/](demos/03-python-keywords-patterns/) | lambda, comprehensions, generators, decorators, `with`/`yield`/`*args` — annotated, runnable, with interview Q&A |
| 4. | Interview question bank | 5 min | [demos/04-interview-question-bank/](demos/04-interview-question-bank/) | Point students to the bank; frame answer structure. Reused in the mock interview later |
| **Second half — the analysis** | | | | |
| 5. | The scenario brief | 5 min | [demos/05-scenario-brief/](demos/05-scenario-brief/) | Present the vague brief; discuss what it *actually* asks for |
| 6. | Plan | 10 min | [demos/06-plan/](demos/06-plan/) | Scope the brief into concrete data/calcs/output decisions, live, from class input |
| 7. | Code — the live analysis | 30 min | [demos/07-code-live-analysis/](demos/07-code-live-analysis/) | Build fetch → analyze → plot with the class; pause constantly to interrogate each line |
| 8. | Review | 10 min | [demos/08-review/](demos/08-review/) | Does the output answer the brief? Where did AI help, where did it need correcting? |
| 9. | Mock interview closer | 15 min | [demos/09-mock-interview/](demos/09-mock-interview/) | Claude as a live mock interviewer on today's work and the whole course |
| 10. | Course wrap-up | 5 min | [demos/10-course-wrap-up/](demos/10-course-wrap-up/) | Recap the full toolkit; how to keep building; end on energy |

Each demo folder has a markdown file with the exact prompts and talking points. Read those, not this table.
Times are a guide — the code step (7) is the heart of the lesson; protect its time.

## The two datasets

The analysis half pulls **live S&P 500 (`^GSPC`) daily prices** from the free Yahoo Finance chart
endpoint via [demos/07-code-live-analysis/fetch_index.py](demos/07-code-live-analysis/fetch_index.py).
A committed **backup** — [backup_sp500_1y.csv](demos/07-code-live-analysis/backup_sp500_1y.csv), real
data 2025-07 → 2026-07 — is the fallback if the live pull fails in class. `analyze_index.py` and
`plot_index.py` use the backup automatically when the live pull hasn't run, so **the lesson never gets
blocked on a network hiccup.** (This is the "have a backup data source ready" note from the plan.)

## The pipeline (the whole course in one picture)

Make this explicit — it's what the capstone demonstrates:

```
Lesson 1:  environment + git
Lesson 2:  plan / code / review  (the AI workflow, used throughout)
Lesson 3:  scrape / pull  ->  clean
Lesson 4:                  clean  ->  analyze  ->  visualize
Lesson 5:  pull  ->  clean  ->  analyze  ->  visualize   (all of it, on a real brief)
```

## The Plan / Code / Review framework

Still the standard workflow — and today it carries the whole analysis:

- **Plan** — turn the vague brief into concrete decisions *before* asking AI to build anything.
- **Code** — let AI generate, but stay in the driver's seat.
- **Review** — never trust unread code; read it, run it, question whether it answers the brief.

## Slides

The `Lesson5_Equity_Analysis_Capstone.pptx` deck lives alongside this README (see Lessons 1–4 for the pattern).

## Homework

None required — the course is complete. See [homework/README.md](homework/README.md) for optional
extensions (repeat the analysis on another index, or run a full mock interview and ask Claude for
structured feedback).

## Setup before class

```bash
pip install -r requirements.txt
```

Uses `pandas`, `numpy`, `matplotlib`, `requests` — all already in `requirements.txt`.

## Notes for the instructor

- **Run the analysis scripts before class** to confirm the live pull still works, and keep the backup
  CSV in place regardless. If Yahoo's endpoint changes on the day, the backup carries the lesson.
- The first half replaces separate "self-review" documents — you're now teaching this material, then
  handing it over as reference. Keep it brisk; it's foundation, not the main event.
- **The code step is the heart of the lesson.** Resist rushing. Pausing to ask "what does this do?"
  and "what could go wrong?" is the point.
- The GitHub issues logged all term feed the opening block — pick the 2–3 richest and work them live.
- **End on energy.** This is the last thing they do before their masters begins. They should leave
  feeling capable.
