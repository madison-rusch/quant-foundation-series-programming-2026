# Lesson 4 — NumPy, Pandas & Data Analysis

2-hour live session. This lesson closes the pipeline started in Lesson 3:
**scrape → clean → analyze → visualize.**

## Running order

| # | Topic | Time | Folder | What happens |
|---|---|---|---|---|
| Opening | Review Lesson 3 homework | 5 min | — | Share scraped datasets, discuss issues; load the class CSV as today's starting point; recap plan/code/review |
| 1. | NumPy — the foundation | 20 min | [demos/01-numpy-foundation/](demos/01-numpy-foundation/) | What NumPy is and why it exists; arrays vs Python lists (typed, vectorized); array creation, slicing, broadcasting, basic math. Brief — its job is to explain *why* Pandas works the way it does |
| 2. | Pandas — working with data | 35 min | [demos/02-pandas-dataframes/](demos/02-pandas-dataframes/) | What a DataFrame is; load the Lesson 3 CSV; head/info/describe, select columns, filter rows, handle missing data, add calculated columns, group and aggregate |
| 3. | Analysis with Pandas | 25 min | [demos/03-analysis/](demos/03-analysis/) | Meaningful calculations on real data: percentage change, rolling averages, comparisons; functions for clean reusable analysis; revisit float precision |
| 4. | Visualization | 20 min | [demos/04-visualization/](demos/04-visualization/) | Just enough matplotlib to produce a clear chart; plot the analyzed data; discuss what it tells us and what decisions it could inform |
| 5. | Interview Angle | 10 min | [demos/05-interview-angle/](demos/05-interview-angle/) | array vs list, what a DataFrame is, handling missing data, vectorization vs loops; Claude as a quick mock interviewer |
| 6. | Common errors (optional) | ~15 min | [demos/06-common-errors/](demos/06-common-errors/) | Overflow / debugging demo: float `==`, silent NaN propagation, chained assignment no-ops, `.loc` vs `.iloc`, NumPy shape mismatch — the failure shapes Review must catch |
| 7. | Useful methods (optional) | ~15 min | [demos/07-useful-methods/](demos/07-useful-methods/) | Overflow demo: `describe`/`value_counts`, `shift`/`diff`/`cumprod`, `np.where`/`clip`, `pd.cut`, `.dt`/`resample` — everyday Pandas vocabulary beyond the core verbs |
| 8. | Flawed analysis (optional) | ~15 min | [demos/08-flawed-analysis/](demos/08-flawed-analysis/) | Overflow demo: code that runs cleanly but reaches the wrong conclusion — cherry-picked window, look-ahead bias in a rolling signal, survivorship bias in the constituents list. Debug the reasoning as a class, not the code |

Each demo folder has a markdown file with the exact prompts and talking points. Read those, not this table.
Demos 6–8 are optional overflow material — pull them in if the core runs short or the class wants more depth.

## The pipeline

Make this arc explicit to the class — it's the whole point of Lessons 3–4:

```
Lesson 3:  scrape  ->  clean
Lesson 4:            clean  ->  analyze  ->  visualize
```

Demo 2 loads the **scraped constituents CSV** from Lesson 3 (grouping by sector). Demos 3–4 use a
bundled **time series** ([demos/02-pandas-dataframes/sample_rates.csv](demos/02-pandas-dataframes/sample_rates.csv))
for percentage change, rolling averages, and plotting — because the constituents list isn't a time
series, and the analysis section needs one.

## Slides

<!-- Deck goes here once finalized: Lesson4_NumPy_Pandas_Data_Analysis.pptx -->
The `.pptx` deck for this lesson is added separately and lives alongside this README (see Lessons 1–2 for the pattern).

## The Plan / Code / Review framework

Still the standard workflow — AI writes the transformations, the class reviews each step:

- **Plan** — define what you want clearly before asking AI to write anything
- **Code** — let AI generate, but stay in the driver's seat
- **Review** — never trust unread code; read it, run it, question it

## Homework

See [homework/README.md](homework/README.md). Extend the analysis with at least one more calculation,
update the visualization, and write a 3–5 sentence stakeholder summary of what your analysis shows.

## Setup before class

```bash
pip install -r requirements.txt
```

Uses `numpy`, `pandas`, `matplotlib` (already in `requirements.txt`).

## Notes for the instructor

- **Have the backup CSVs ready.** If students' Lesson 3 scrapers produced broken data, a shared
  dataset avoids burning class time on cleaning. The bundled
  [sample_rates.csv](demos/02-pandas-dataframes/sample_rates.csv) and the Lesson 3
  [backup_sp500.csv](../lesson-03-python-fundamentals/homework/scripts/backup_sp500.csv) both work standalone.
- The NumPy section is intentionally brief — motivate Pandas, don't teach NumPy exhaustively.
- **Pandas is the core of this lesson** — spend the most energy on Demo 2.
- The visualization section closes the scrape→clean→analyze→visualize arc. Make that explicit.
- Revisit float precision briefly in the analysis section — students saw it in Lesson 3; it deserves
  reinforcement in a Pandas context.
