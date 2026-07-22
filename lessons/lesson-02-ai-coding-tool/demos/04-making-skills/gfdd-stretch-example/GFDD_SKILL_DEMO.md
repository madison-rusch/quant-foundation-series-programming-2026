# Stretch Example — A Skill for a Real Messy Dataset

Optional, if time allows after the main Demo 4 skill-building exercise (or assign as a follow-up).
Uses a real public dataset instead of the bond examples used elsewhere in this lesson, to show
that skills matter most on data you didn't design yourself.

## The dataset

**World Bank Global Financial Development Database (GFDD)** — 108 financial-system indicators
(depth, access, efficiency, stability of financial institutions and markets) across 214 economies,
1960–2021.

Download page: https://www.worldbank.org/en/publication/gfdr/data/global-financial-development-database

Direct file (verified working — 14.4 MB):
```
https://thedocs.worldbank.org/en/doc/5882f2b2117b882d58a78f9c64ea3613-0050062022/original/20220909-global-financial-development-database.xlsx
```

**Gotcha to demo live if you want a laugh:** this URL 404s on a `HEAD` request (`curl -I`) but
works fine on a normal `GET` (`curl -o file.xlsx <url>`, or just opening it in a browser). Some
tools and libraries check a URL with `HEAD` first — if a student's download script mysteriously
fails, this is a real-world reason why. It's also a small, honest example of "unclean" starting
one step before you even open the file.

## What's actually in the workbook (verified by opening it)

| Sheet | Contents |
|---|---|
| `Summary` | Mostly blank — a cover sheet |
| `Metadata` | 113 rows: `Topic`, `Indicator Code` (e.g. `GFDD.AI.01`), `Indicator Name`, `Short Definition`, `Long Definition`, `Coverage` (e.g. `2004-2021`, or sparse years like `2011, 2014, 2017, 2021`) |
| `Data - August 2022` | 13,269 rows × 115 columns: `iso3, iso2, imfn, country, region, income, year`, then indicator columns |
| `Metadata - 2021` | The metadata sheet for the older data vintage |
| `Data - November 2021` | 13,055 rows × **122** columns — a different, older data release |

Three concrete messes to point out live:

1. **The data sheet's column headers don't match the metadata sheet's indicator codes.**
   The `Data - August 2022` sheet uses bare lowercase codes like `ai01`, `ai02`; the `Metadata`
   sheet lists them as `GFDD.AI.01`, `GFDD.AI.02`. You have to reconcile these yourself before you
   can say what any column means.
2. **Two data vintages, different shapes.** `Data - August 2022` has 115 columns;
   `Data - November 2021` has 122. Naively concatenating or comparing them column-by-column
   without checking headers first will misalign indicators.
3. **Heavy, structured missingness.** Even a large, well-covered economy like the United States
   has plenty of `None` cells — because each indicator's `Coverage` window (from the metadata) is
   different, not because data was lost. Pull a real row live:

   ```python
   import openpyxl
   wb = openpyxl.load_workbook("gfdd.xlsx", read_only=True, data_only=True)
   ws = wb["Data - August 2022"]
   for row in ws.iter_rows(min_row=2, values_only=True):
       if row[3] == "United States" and row[6] == 2021:
           print(row[:12])
           break
   ```

   ```
   ('USA', 'US', 111, 'United States', 'North America', 'High income', 2021, None, 138.25501, None, None, None, 94.95323)
   ```

   Several `None`s in a row for a country with excellent data reporting — that's the coverage
   window at work, not a data quality failure.

## Part A — Without the skill

Prompt Claude with no skill loaded:

```
Load this GFDD Excel file and tell me the average value of column ai02 by region for the most
recent year available.
```

Watch for what it *doesn't* ask: which sheet, which vintage, what `ai02` even means, or whether
"most recent year available" is the same year for every country. A plausible-looking number can
come back with several of the mess points above silently baked in.

## Part B — With the `financial-dataset-cleaning` skill loaded

Same prompt, skill loaded (see `financial-dataset-cleaning-skill.md` in this folder):

```
Using the financial-dataset-cleaning skill, load this GFDD Excel file and tell me the average
value of indicator ai02 (bank branches per 100,000 adults) by region for the most recent year
with broad coverage.
```

Expect the response to now explicitly: name which sheet/vintage it used, cross-reference `ai02`
against the `Metadata` sheet, flag that "most recent year" varies by country and pick a defensible
single year instead, and report how many countries had data for that year (not silently averaging
over however many happened to respond).

## Talking points

- This is the same Plan/Code/Review instinct from Demo 3, applied to data instead of a formula —
  the "plan" here is knowing what questions to ask *about the data* before asking a question *of*
  the data.
- Real datasets don't announce their own inconsistencies. A skill is how you make sure the same
  checks happen every time, instead of only when you happen to remember.
- None of this is about the World Bank specifically — the same five rules apply to any FRED,
  IMF, SEC, or vendor multi-sheet export a student will meet after this course.
