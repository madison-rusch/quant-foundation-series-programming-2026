# Lesson 3 — Python Fundamentals via Web Scraping

2-hour live session.

## Running order

| # | Topic | Time | Folder | What happens |
|---|---|---|---|---|
| Opening | Review Lesson 2 homework | 5 min | — | What did students notice when they refined their prompts? What changed in the output? Recap plan/code/review as today's working method |
| 1. | Python Fundamentals | 40 min | [demos/01-python-fundamentals/](demos/01-python-fundamentals/) | Data types; float precision (`0.1 + 0.2 != 0.3`) and why it matters in finance; control flow; functions; try/except; mutable vs immutable; variables as references. Taught by **reading and annotating** short snippets, not writing from scratch |
| 2. | Scraping with BeautifulSoup | 35 min | [demos/02-scraping-beautifulsoup/](demos/02-scraping-beautifulsoup/) | What scraping is and when it's useful; install/import BeautifulSoup; live scrape of a financially relevant public page; plan/code/review the scraper as a class; **save to CSV for Lesson 4**; discuss what can go wrong |
| 3. | Interview Angle | 30 min | [demos/03-interview-angle/](demos/03-interview-angle/) | Common Python/CS interview questions tied to today's topics (list vs tuple, mutability, references, try/except, list vs dict, functions); how to answer clearly; Claude as a mock interviewer, critiqued as a class |

Each demo folder has a markdown file with the exact prompts and talking points. Read those, not this table.

## Slides

<!-- Deck goes here once finalized: Lesson3_Python_Fundamentals.pptx -->
The `.pptx` deck for this lesson is added separately and lives alongside this README (see Lessons 1–2 for the pattern).

## The Plan / Code / Review framework

Still the standard workflow — reinforce it every lesson:

- **Plan** — define what you want clearly before asking AI to write anything
- **Code** — let AI generate, but stay in the driver's seat
- **Review** — never trust unread code; read it, run it, question it

## Homework

See [homework/README.md](homework/README.md). Extend the in-class scraper to pull at least one
more data point, save it cleanly to a CSV **for use in Lesson 4**, and explain in plain English
what your scraper does.

## Setup before class

Same environment as before. Lessons 3–4 add a few packages — make sure your virtual environment
is up to date:

```bash
pip install -r requirements.txt
```

New this lesson: `requests`, `beautifulsoup4`, `lxml`.

## Notes for the instructor

- **Pre-select and pre-run the scrape source before class.** Sites change and a broken demo is
  hard to recover from live. The demo targets a stable Wikipedia table; keep a backup source and a
  pre-saved CSV ready anyway (see [homework/scripts/](homework/scripts/)).
- The fundamentals block is the longest single stretch in the course — keep it moving with short
  annotated snippets rather than long explanations.
- Mutable vs immutable and references-vs-copies produce "aha" moments for non-CS students. Give them
  space, but aim for intuition, not a CS degree.
- Make sure everyone leaves with a CSV — **Lesson 4 depends on it.** A shared backup CSV is bundled.
